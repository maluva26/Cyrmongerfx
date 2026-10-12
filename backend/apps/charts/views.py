import hmac
import time
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.core.constants import CONFIDENCE_NOTE, DISCLAIMER
from apps.core.permissions import IsTrader
from apps.core.responses import error_response
from apps.inference.constants import ALLOWED_PATTERNS
from apps.inference.detectors import ModelUnavailable, get_active_detector
from apps.inference.explanations import create_educational_explanation
from apps.inference.preprocess import InvalidImage, safely_decode
from apps.inference.signals import generate_signal

from .models import Analysis, ChartUpload, Detection
from .serializers import AnalysisSerializer, ChartUploadSerializer
from .storage import StorageUnavailable, get_chart_storage


def _extension(mime: str) -> str:
    return {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp"}.get(mime, "img")


def _valid_box(box) -> bool:
    if not isinstance(box, (list, tuple)) or len(box) != 4:
        return False
    x_min, y_min, x_max, y_max = [float(value) for value in box]
    return 0 <= x_min < x_max <= 1 and 0 <= y_min < y_max <= 1


class AnalyzeChartView(APIView):
    permission_classes = [IsTrader]
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "analyze"

    @extend_schema(description="Upload a chart image and run educational pattern analysis.")
    @transaction.atomic
    def post(self, request):
        upload = request.FILES.get("image")
        if not upload:
            return error_response("UPLOAD_REQUIRED", "Please upload a chart image.", status.HTTP_400_BAD_REQUEST)
        max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
        if upload.size > max_bytes:
            return error_response("FILE_TOO_LARGE", f"Upload must be {settings.MAX_UPLOAD_MB} MB or smaller.", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        raw = upload.read()
        try:
            _image, mime_type = safely_decode(raw)
        except InvalidImage:
            return error_response("INVALID_IMAGE", "The file could not be read as a chart image.", status.HTTP_400_BAD_REQUEST)
        if mime_type not in settings.ALLOWED_IMAGE_TYPES:
            return error_response("UNSUPPORTED_FILE_TYPE", "Only PNG, JPEG and WebP chart images are supported.", status.HTTP_400_BAD_REQUEST)

        retention_until = timezone.now() + timedelta(days=settings.CHART_RETENTION_DAYS)
        chart = ChartUpload.objects.create(
            user=request.user,
            instrument=request.data.get("instrument") or None,
            timeframe=request.data.get("timeframe") or None,
            mime_type=mime_type,
            size_bytes=len(raw),
            retention_until=retention_until,
        )
        analysis = Analysis.objects.create(chart=chart, model_version=settings.MODEL_VERSION or "unknown")
        storage_ref = f"{request.user.pk}/{chart.chart_id}.{_extension(mime_type)}"
        try:
            chart.storage_ref = get_chart_storage().upload(storage_ref, raw, mime_type)
            chart.save(update_fields=["storage_ref"])
        except StorageUnavailable:
            analysis.status = Analysis.Status.FAILED
            analysis.summary = "Chart storage is unavailable. Please try again later."
            analysis.save(update_fields=["status", "summary"])
            return error_response("STORAGE_UNAVAILABLE", analysis.summary, status.HTTP_503_SERVICE_UNAVAILABLE)

        started = time.perf_counter()
        try:
            detector = get_active_detector()
            detections = detector.predict(raw)
        except ModelUnavailable as exc:
            analysis.status = Analysis.Status.FAILED
            analysis.summary = str(exc)
            analysis.save(update_fields=["status", "summary"])
            return error_response("MODEL_UNAVAILABLE", str(exc), status.HTTP_503_SERVICE_UNAVAILABLE)

        filtered = []
        for detection in detections:
            if detection.get("label") not in ALLOWED_PATTERNS:
                continue
            confidence = float(detection.get("confidence", 0))
            if confidence < settings.MIN_CONFIDENCE_THRESHOLD or not _valid_box(detection.get("box")):
                continue
            filtered.append({"label": detection["label"], "confidence": confidence, "box": detection["box"]})

        if not filtered:
            analysis.status = Analysis.Status.COMPLETED_NO_DETECTION
            analysis.signal_category = Analysis.Signal.NEUTRAL
            analysis.summary = create_educational_explanation([])
            analysis.processing_ms = int((time.perf_counter() - started) * 1000)
            analysis.model_version = getattr(detector, "version", settings.MODEL_VERSION)
            chart.status = ChartUpload.Status.PROCESSED
            chart.save(update_fields=["status"])
            analysis.save()
        else:
            for detection in filtered:
                x_min, y_min, x_max, y_max = detection["box"]
                Detection.objects.create(
                    analysis=analysis,
                    label=detection["label"],
                    confidence=detection["confidence"],
                    x_min=x_min,
                    y_min=y_min,
                    x_max=x_max,
                    y_max=y_max,
                )
            signal, confidence = generate_signal(filtered)
            analysis.status = Analysis.Status.COMPLETED
            analysis.signal_category = signal
            analysis.overall_confidence = confidence
            analysis.summary = create_educational_explanation(filtered)
            analysis.processing_ms = int((time.perf_counter() - started) * 1000)
            analysis.model_version = getattr(detector, "version", settings.MODEL_VERSION)
            chart.status = ChartUpload.Status.PROCESSED
            chart.save(update_fields=["status"])
            analysis.save()

        payload = AnalysisSerializer(analysis).data
        payload["chart_id"] = str(chart.chart_id)
        payload["explanation"] = payload.pop("summary")
        return Response(payload, status=status.HTTP_201_CREATED)


class ChartListView(APIView):
    def get(self, request):
        queryset = ChartUpload.objects.filter(user=request.user)
        if request.query_params.get("instrument"):
            queryset = queryset.filter(instrument__iexact=request.query_params["instrument"])
        if request.query_params.get("signal"):
            queryset = queryset.filter(analyses__signal_category=request.query_params["signal"]).distinct()
        page = self.paginate_queryset(queryset)
        serializer = ChartUploadSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def paginate_queryset(self, queryset):
        from apps.core.pagination import StandardPageNumberPagination

        self.paginator = StandardPageNumberPagination()
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        return self.paginator.get_paginated_response(data)


class ChartDetailView(APIView):
    def get_object(self, request, chart_id):
        return ChartUpload.objects.filter(user=request.user, chart_id=chart_id).first()

    def get(self, request, chart_id):
        chart = self.get_object(request, chart_id)
        if not chart:
            return error_response("NOT_FOUND", "Chart not found.", status.HTTP_404_NOT_FOUND)
        return Response(ChartUploadSerializer(chart).data)

    def delete(self, request, chart_id):
        chart = self.get_object(request, chart_id)
        if not chart:
            return error_response("NOT_FOUND", "Chart not found.", status.HTTP_404_NOT_FOUND)
        if chart.storage_ref:
            try:
                get_chart_storage().delete(chart.storage_ref)
            except Exception:
                pass
        chart.storage_ref = None
        chart.status = ChartUpload.Status.REMOVED
        chart.save(update_fields=["storage_ref", "status"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class AnalysisDetailView(APIView):
    def get(self, request, analysis_id):
        analysis = Analysis.objects.filter(chart__user=request.user, analysis_id=analysis_id).first()
        if not analysis:
            return error_response("NOT_FOUND", "Analysis not found.", status.HTTP_404_NOT_FOUND)
        return Response(AnalysisSerializer(analysis).data)


class ModelInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "model_version": settings.MODEL_VERSION,
                "is_demo_model": (settings.MODEL_VERSION or "").startswith("mock"),
                "classes": ALLOWED_PATTERNS,
                "disclaimer": DISCLAIMER,
                "confidence_note": CONFIDENCE_NOTE,
            }
        )


class InternalPurgeView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "internal"

    def post(self, request):
        provided = request.headers.get("X-Internal-Cron-Token", "")
        expected = settings.INTERNAL_CRON_TOKEN or "unset"
        if not settings.INTERNAL_CRON_TOKEN or not hmac.compare_digest(provided, expected):
            return error_response("NOT_FOUND", "Not found.", status.HTTP_404_NOT_FOUND)
        removed = 0
        for chart in ChartUpload.objects.filter(retention_until__lt=timezone.now()).exclude(status=ChartUpload.Status.REMOVED):
            if chart.storage_ref:
                try:
                    get_chart_storage().delete(chart.storage_ref)
                except Exception:
                    pass
            chart.storage_ref = None
            chart.status = ChartUpload.Status.REMOVED
            chart.save(update_fields=["storage_ref", "status"])
            removed += 1
        return Response({"removed": removed})

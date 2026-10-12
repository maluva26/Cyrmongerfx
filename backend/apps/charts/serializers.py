from django.conf import settings
from rest_framework import serializers

from apps.core.constants import CONFIDENCE_NOTE, DISCLAIMER

from .models import Analysis, ChartUpload, Detection
from .storage import get_chart_storage


class DetectionSerializer(serializers.ModelSerializer):
    box = serializers.SerializerMethodField()
    below_display_threshold = serializers.SerializerMethodField()

    class Meta:
        model = Detection
        fields = ["detection_id", "label", "confidence", "box", "below_display_threshold"]

    def get_box(self, obj):
        return [obj.x_min, obj.y_min, obj.x_max, obj.y_max]

    def get_below_display_threshold(self, obj):
        return float(obj.confidence) < settings.DISPLAY_CONFIDENCE_THRESHOLD


class AnalysisSerializer(serializers.ModelSerializer):
    detections = DetectionSerializer(many=True, read_only=True)
    disclaimer = serializers.SerializerMethodField()
    confidence_note = serializers.SerializerMethodField()
    is_demo_model = serializers.SerializerMethodField()

    class Meta:
        model = Analysis
        fields = [
            "analysis_id",
            "chart_id",
            "model_version",
            "is_demo_model",
            "status",
            "signal_category",
            "overall_confidence",
            "summary",
            "detections",
            "processing_ms",
            "disclaimer",
            "confidence_note",
        ]

    def get_disclaimer(self, obj):
        return DISCLAIMER

    def get_confidence_note(self, obj):
        return CONFIDENCE_NOTE

    def get_is_demo_model(self, obj):
        return obj.model_version.startswith("mock")


class ChartUploadSerializer(serializers.ModelSerializer):
    latest_analysis = serializers.SerializerMethodField()
    signed_image_url = serializers.SerializerMethodField()

    class Meta:
        model = ChartUpload
        fields = [
            "chart_id",
            "instrument",
            "timeframe",
            "mime_type",
            "status",
            "uploaded_at",
            "retention_until",
            "signed_image_url",
            "latest_analysis",
        ]

    def get_latest_analysis(self, obj):
        analysis = obj.analyses.first()
        return AnalysisSerializer(analysis).data if analysis else None

    def get_signed_image_url(self, obj):
        if not obj.storage_ref or obj.status == ChartUpload.Status.REMOVED:
            return None
        try:
            return get_chart_storage().signed_url(obj.storage_ref)
        except Exception:
            return None

import io
from unittest.mock import patch

from PIL import Image
from rest_framework import status

from apps.charts.models import ChartUpload
from apps.core.constants import CONFIDENCE_NOTE, DISCLAIMER


def _png():
    buf = io.BytesIO()
    Image.new("RGB", (50, 50), "white").save(buf, "PNG")
    buf.seek(0)
    return buf


def _large_png():
    """Incompressible noise image, comfortably bigger than 1 KB once encoded."""
    buf = io.BytesIO()
    Image.effect_noise((400, 400), 100).convert("RGB").save(buf, "PNG")
    buf.seek(0)
    return buf


class TestCharts:
    def test_analyze_valid(self, trader_client):
        buf = _png()
        r = trader_client.post("/api/v1/charts/analyze", {"image": buf}, format="multipart")
        assert r.status_code == status.HTTP_201_CREATED
        data = r.json()
        assert "analysis_id" in data
        assert data["disclaimer"] == DISCLAIMER

    def test_oversize(self, trader_client, settings):
        settings.MAX_UPLOAD_MB = 0.001
        buf = _large_png()
        r = trader_client.post("/api/v1/charts/analyze", {"image": buf}, format="multipart")
        assert r.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        assert r.json()["error"]["code"] == "FILE_TOO_LARGE"

    def test_corrupt_file(self, trader_client):
        r = trader_client.post("/api/v1/charts/analyze", {"image": io.BytesIO(b"notanimage")}, format="multipart")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert r.json()["error"]["code"] == "INVALID_IMAGE"

    def test_unsupported_type(self, trader_client):
        buf = io.BytesIO(b"MZ" + b"\x00" * 100)
        r = trader_client.post("/api/v1/charts/analyze", {"image": buf}, format="multipart")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert r.json()["error"]["code"] == "INVALID_IMAGE"

    def test_model_unavailable(self, trader_client):
        with patch("apps.charts.views.get_active_detector") as mock:
            from apps.inference.detectors import ModelUnavailable

            mock.side_effect = ModelUnavailable("down")
            buf = _png()
            r = trader_client.post("/api/v1/charts/analyze", {"image": buf}, format="multipart")
            assert r.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    def test_no_detection(self, trader_client):
        with patch("apps.charts.views.get_active_detector") as mock:
            mock.return_value.predict.return_value = []
            mock.return_value.version = "mock-0.1"
            buf = _png()
            r = trader_client.post("/api/v1/charts/analyze", {"image": buf}, format="multipart")
            assert r.status_code == status.HTTP_201_CREATED
            assert r.json()["status"] == "COMPLETED_NO_DETECTION"

    def test_ownership_chart(self, other_client, user):
        chart = ChartUpload.objects.create(user=user, mime_type="image/png", size_bytes=10)
        r = other_client.get(f"/api/v1/charts/{chart.chart_id}")
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_demo_model_banner(self, trader_client, settings):
        settings.MODEL_VERSION = "mock-0.1"
        buf = _png()
        r = trader_client.post("/api/v1/charts/analyze", {"image": buf}, format="multipart")
        assert r.json()["is_demo_model"] is True

    def test_detection_persisted_and_returned(self, trader_client):
        """TC-06: a detection above threshold is stored and returned with a signal."""
        with patch("apps.charts.views.get_active_detector") as mock:
            mock.return_value.version = "mock-0.1"
            mock.return_value.predict.return_value = [{"label": "double_top", "confidence": 0.91, "box": [0.1, 0.2, 0.6, 0.7]}]
            r = trader_client.post("/api/v1/charts/analyze", {"image": _png()}, format="multipart")
        assert r.status_code == status.HTTP_201_CREATED
        data = r.json()
        assert data["status"] == "COMPLETED"
        assert data["signal_category"] == "SELL"
        assert len(data["detections"]) == 1
        assert data["detections"][0]["label"] == "double_top"
        assert data["detections"][0]["box"] == [0.1, 0.2, 0.6, 0.7]
        assert data["disclaimer"] == DISCLAIMER
        assert data["confidence_note"] == CONFIDENCE_NOTE
        assert "explanation" in data

    def test_low_confidence_detection_dropped(self, trader_client, settings):
        settings.MIN_CONFIDENCE_THRESHOLD = 0.80
        with patch("apps.charts.views.get_active_detector") as mock:
            mock.return_value.version = "mock-0.1"
            mock.return_value.predict.return_value = [{"label": "double_top", "confidence": 0.55, "box": [0.1, 0.2, 0.6, 0.7]}]
            r = trader_client.post("/api/v1/charts/analyze", {"image": _png()}, format="multipart")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.json()["status"] == "COMPLETED_NO_DETECTION"
        assert r.json()["detections"] == []

    def test_renamed_executable_rejected(self, trader_client):
        """SEC-04: a non-image payload wearing a .png name must be rejected."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        upload = SimpleUploadedFile("chart.png", b"MZ" + b"\x00" * 512, content_type="image/png")
        r = trader_client.post("/api/v1/charts/analyze", {"image": upload}, format="multipart")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert r.json()["error"]["code"] == "INVALID_IMAGE"

    def test_chart_list_and_analysis_detail(self, trader_client):
        with patch("apps.charts.views.get_active_detector") as mock:
            mock.return_value.version = "mock-0.1"
            mock.return_value.predict.return_value = [{"label": "double_top", "confidence": 0.91, "box": [0.1, 0.2, 0.6, 0.7]}]
            created = trader_client.post("/api/v1/charts/analyze", {"image": _png(), "instrument": "EUR/USD"}, format="multipart").json()
        listing = trader_client.get("/api/v1/charts")
        assert listing.status_code == status.HTTP_200_OK
        assert listing.json()["count"] >= 1
        detail = trader_client.get(f"/api/v1/charts/{created['chart_id']}")
        assert detail.status_code == status.HTTP_200_OK
        analysis = trader_client.get(f"/api/v1/analyses/{created['analysis_id']}")
        assert analysis.status_code == status.HTTP_200_OK
        assert analysis.json()["signal_category"] == "SELL"

    def test_missing_upload_rejected(self, trader_client):
        r = trader_client.post("/api/v1/charts/analyze", {}, format="multipart")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert r.json()["error"]["code"] == "UPLOAD_REQUIRED"

    def test_model_info_public(self, client):
        r = client.get("/api/v1/model")
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["disclaimer"] == DISCLAIMER

    def test_internal_purge_requires_token(self, client):
        r = client.post("/api/v1/internal/purge")
        assert r.status_code == status.HTTP_404_NOT_FOUND

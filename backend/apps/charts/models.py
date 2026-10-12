import uuid

from django.conf import settings
from django.db import models


class ChartUpload(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSED = "PROCESSED", "Processed"
        REJECTED = "REJECTED", "Rejected"
        REMOVED = "REMOVED", "Removed"

    chart_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chart_uploads")
    storage_ref = models.CharField(max_length=500, blank=True, null=True)
    instrument = models.CharField(max_length=40, blank=True, null=True)
    timeframe = models.CharField(max_length=20, blank=True, null=True)
    mime_type = models.CharField(max_length=80)
    size_bytes = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    retention_until = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "chart_upload"
        ordering = ["-uploaded_at"]
        indexes = [models.Index(fields=["user", "-uploaded_at"])]


class Analysis(models.Model):
    class Status(models.TextChoices):
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        COMPLETED_NO_DETECTION = "COMPLETED_NO_DETECTION", "Completed no detection"
        FAILED = "FAILED", "Failed"
        REJECTED = "REJECTED", "Rejected"

    class Signal(models.TextChoices):
        BUY = "BUY", "Buy"
        SELL = "SELL", "Sell"
        NEUTRAL = "NEUTRAL", "Neutral"

    analysis_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chart = models.ForeignKey(ChartUpload, on_delete=models.CASCADE, related_name="analyses")
    model_version = models.CharField(max_length=60)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PROCESSING)
    overall_confidence = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    signal_category = models.CharField(max_length=10, choices=Signal.choices, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    processing_ms = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analysis"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["chart"])]


class Detection(models.Model):
    detection_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name="detections")
    label = models.CharField(max_length=80)
    confidence = models.DecimalField(max_digits=5, decimal_places=4)
    x_min = models.DecimalField(max_digits=8, decimal_places=6)
    y_min = models.DecimalField(max_digits=8, decimal_places=6)
    x_max = models.DecimalField(max_digits=8, decimal_places=6)
    y_max = models.DecimalField(max_digits=8, decimal_places=6)

    class Meta:
        db_table = "detection"
        indexes = [models.Index(fields=["analysis"])]
        constraints = [
            models.CheckConstraint(condition=models.Q(confidence__gte=0) & models.Q(confidence__lte=1), name="detection_confidence_0_1"),
            models.CheckConstraint(condition=models.Q(x_min__lt=models.F("x_max")), name="detection_x_min_lt_x_max"),
            models.CheckConstraint(condition=models.Q(y_min__lt=models.F("y_max")), name="detection_y_min_lt_y_max"),
        ]

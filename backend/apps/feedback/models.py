import uuid

from django.conf import settings
from django.db import models

from apps.charts.models import Analysis


class Feedback(models.Model):
    class Type(models.TextChoices):
        WRONG_DETECTION = "WRONG_DETECTION", "Wrong detection"
        ACCESSIBILITY = "ACCESSIBILITY", "Accessibility"
        UPLOAD_FAILURE = "UPLOAD_FAILURE", "Upload failure"
        CONTENT_UNCLEAR = "CONTENT_UNCLEAR", "Content unclear"
        OTHER = "OTHER", "Other"

    feedback_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedback")
    type = models.CharField(max_length=40, choices=Type.choices)
    analysis = models.ForeignKey(Analysis, null=True, blank=True, on_delete=models.SET_NULL)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "feedback"
        ordering = ["-created_at"]

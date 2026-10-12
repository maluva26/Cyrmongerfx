import uuid

from django.conf import settings
from django.db import models

from apps.charts.models import Analysis


class JournalEntry(models.Model):
    entry_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="journal_entries")
    analysis = models.ForeignKey(Analysis, null=True, blank=True, on_delete=models.SET_NULL, related_name="journal_entries")
    notes = models.TextField(blank=True, null=True)
    outcome_value = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)
    outcome_currency = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "journal_entry"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]

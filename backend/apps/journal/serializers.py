from rest_framework import serializers

from apps.charts.models import Analysis

from .models import JournalEntry


class JournalEntrySerializer(serializers.ModelSerializer):
    note = serializers.SerializerMethodField()

    class Meta:
        model = JournalEntry
        fields = ["entry_id", "analysis", "notes", "outcome_value", "outcome_currency", "created_at", "updated_at", "note"]
        read_only_fields = ["entry_id", "created_at", "updated_at", "note"]

    def get_note(self, obj):
        return "Personal notes, not a broker statement."

    def validate_analysis(self, value):
        request = self.context["request"]
        if value and not Analysis.objects.filter(analysis_id=value.analysis_id, chart__user=request.user).exists():
            raise serializers.ValidationError("Analysis not found.")
        return value

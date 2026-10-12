from rest_framework import serializers

from apps.charts.models import Analysis

from .models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["feedback_id", "type", "analysis", "message", "created_at"]
        read_only_fields = ["feedback_id", "created_at"]

    def validate_analysis(self, value):
        if value and not Analysis.objects.filter(analysis_id=value.analysis_id, chart__user=self.context["request"].user).exists():
            raise serializers.ValidationError("Analysis not found.")
        return value

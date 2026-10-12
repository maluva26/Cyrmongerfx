from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.charts.models import ChartUpload
from apps.charts.storage import get_chart_storage


class Command(BaseCommand):
    help = "Remove expired chart uploads."

    def handle(self, *args, **options):
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
        self.stdout.write(self.style.SUCCESS(f"Removed {removed} charts."))

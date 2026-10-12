from decimal import Decimal

from django.db.models import Count, Avg
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from apps.charts.models import Analysis
from apps.journal.models import JournalEntry
from apps.learning.models import Lesson, QuizAttempt
from apps.risk.models import RiskPlan


class DashboardView(APIView):
    def get(self, request):
        user = request.user
        recent_analyses = Analysis.objects.filter(chart__user=user).order_by("-created_at")[:5]
        recent_journal = JournalEntry.objects.filter(user=user).order_by("-created_at")[:5]
        recent_plans = RiskPlan.objects.filter(user=user).order_by("-created_at")[:3]
        published = Lesson.objects.filter(status=Lesson.Status.PUBLISHED)
        best = QuizAttempt.objects.filter(user=user, lesson__in=published).values("lesson_id").annotate(best_score=Avg("score"))
        lessons_completed = sum(1 for item in best if item["best_score"] >= Decimal("70"))
        analyses_this_month = Analysis.objects.filter(chart__user=user, created_at__gte=timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)).count()
        return Response(
            {
                "kpis": {
                    "lessons_completed": lessons_completed,
                    "lessons_total": published.count(),
                    "average_quiz_score": round(sum(item["best_score"] for item in best) / len(best), 2) if best else 0,
                    "analyses_this_month": analyses_this_month,
                },
                "recent_analyses": [
                    {
                        "analysis_id": str(a.analysis_id),
                        "signal_category": a.signal_category,
                        "overall_confidence": a.overall_confidence,
                        "created_at": a.created_at.isoformat(),
                    }
                    for a in recent_analyses
                ],
                "recent_journal": [
                    {
                        "entry_id": str(e.entry_id),
                        "notes": e.notes[:120] if e.notes else "",
                        "created_at": e.created_at.isoformat(),
                    }
                    for e in recent_journal
                ],
                "recent_risk_plans": [
                    {
                        "risk_plan_id": str(p.risk_plan_id),
                        "instrument": p.instrument,
                        "risk_amount": str(p.risk_amount),
                        "created_at": p.created_at.isoformat(),
                    }
                    for p in recent_plans
                ],
            }
        )


class ActivityReportView(APIView):
    def get(self, request):
        user = request.user
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        qs = Analysis.objects.filter(chart__user=user)
        if from_date:
            qs = qs.filter(created_at__gte=from_date)
        if to_date:
            qs = qs.filter(created_at__lte=to_date)
        by_signal = qs.values("signal_category").annotate(count=Count("analysis_id"))
        by_pattern = Analysis.objects.filter(chart__user=user).values("detections__label").annotate(count=Count("analysis_id")).order_by("-count")[:10]
        quiz_qs = QuizAttempt.objects.filter(user=user)
        if from_date:
            quiz_qs = quiz_qs.filter(completed_at__gte=from_date)
        if to_date:
            quiz_qs = quiz_qs.filter(completed_at__lte=to_date)
        quiz_summary = quiz_qs.aggregate(avg_score=Avg("score"), count=Count("attempt_id"))
        lessons_completed = QuizAttempt.objects.filter(user=user, score__gte=Decimal("70")).values("lesson_id").distinct().count()
        journal_count = JournalEntry.objects.filter(user=user)
        if from_date:
            journal_count = journal_count.filter(created_at__gte=from_date)
        if to_date:
            journal_count = journal_count.filter(created_at__lte=to_date)
        journal_count = journal_count.count()
        return Response(
            {
                "period": {"from": from_date, "to": to_date},
                "analyses_by_signal": list(by_signal),
                "analyses_by_pattern": list(by_pattern),
                "quiz": quiz_summary,
                "lessons_completed": lessons_completed,
                "journal_entries": journal_count,
            }
        )


class ExportReportView(APIView):
    def get(self, request):
        fmt = request.query_params.get("format", "csv").lower()
        report_data = ActivityReportView().get(request).data
        if fmt == "pdf":
            return self._pdf(report_data)
        return self._csv(report_data)

    def _csv(self, data):
        from django.http import HttpResponse
        import csv

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="report.csv"'
        writer = csv.writer(response)
        writer.writerow(["Cyrmonger Algo Fx Activity Report"])
        writer.writerow([f"Generated at: {timezone.now().isoformat()}"])
        writer.writerow(["This report summarizes your activity on this platform. It is not a broker statement or a guarantee of performance."])
        writer.writerow([])
        writer.writerow(["Analyses by signal"])
        for row in data.get("analyses_by_signal", []):
            writer.writerow([row.get("signal_category"), row.get("count")])
        writer.writerow([])
        writer.writerow(["Analyses by pattern"])
        for row in data.get("analyses_by_pattern", []):
            writer.writerow([row.get("detections__label"), row.get("count")])
        writer.writerow([])
        writer.writerow(["Quiz summary"])
        quiz = data.get("quiz", {})
        writer.writerow(["Average score", quiz.get("avg_score")])
        writer.writerow(["Attempts", quiz.get("count")])
        writer.writerow(["Lessons completed", data.get("lessons_completed")])
        writer.writerow(["Journal entries", data.get("journal_entries")])
        return response

    def _pdf(self, data):
        from django.http import HttpResponse

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="report.pdf"'
        doc = SimpleDocTemplate(response, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = [Paragraph("Cyrmonger Algo Fx Activity Report", styles["Title"]), Spacer(1, 12)]
        elements.append(Paragraph(f"Generated at: {timezone.now().isoformat()}", styles["Normal"]))
        elements.append(Paragraph("This report summarizes your activity on this platform. It is not a broker statement or a guarantee of performance.", styles["Normal"]))
        elements.append(Spacer(1, 12))
        table_data = [["Signal", "Count"]] + [[r.get("signal_category"), r.get("count")] for r in data.get("analyses_by_signal", [])]
        elements.append(
            Table(table_data, style=TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.grey), ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke), ("GRID", (0, 0), (-1, -1), 1, colors.black)]))
        )
        doc.build(elements)
        return response

from decimal import Decimal

from django.db import transaction
from django.db.models import Avg, Count, Max, Prefetch, Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.core.models import audit
from apps.core.permissions import IsAdminRole
from apps.core.responses import error_response

from .models import Lesson, LessonResource, QuizAttempt, QuizOption, QuizQuestion
from .serializers import (
    AdminLessonSerializer,
    AdminLessonResourceCreateSerializer,
    AdminQuizQuestionSerializer,
    LessonDetailSerializer,
    LessonResourceSerializer,
    LessonListSerializer,
    QuizSubmitSerializer,
)
from .starter_modules import STARTER_MODULES, STARTER_MODULES_BY_KEY


def lessons_with_quiz_data():
    questions = QuizQuestion.objects.select_related("lesson").prefetch_related("options")
    resources = LessonResource.objects.select_related("lesson")
    return Lesson.objects.prefetch_related(
        Prefetch("questions", queryset=questions),
        Prefetch("resources", queryset=resources),
    )


class LessonListView(APIView):
    def get(self, request):
        queryset = Lesson.objects.filter(status=Lesson.Status.PUBLISHED)
        if request.query_params.get("category"):
            queryset = queryset.filter(category__iexact=request.query_params["category"])
        data = LessonListSerializer(queryset, many=True).data
        return Response(data)


class LessonDetailView(APIView):
    def get(self, request, lesson_id):
        lesson = get_object_or_404(
            lessons_with_quiz_data(),
            lesson_id=lesson_id,
            status=Lesson.Status.PUBLISHED,
        )
        return Response(LessonDetailSerializer(lesson).data)


class LessonMaterialDownloadView(APIView):
    def get(self, request, lesson_id, resource_id):
        resource = get_object_or_404(
            LessonResource.objects.select_related("lesson"),
            lesson_id=lesson_id,
            resource_id=resource_id,
            kind=LessonResource.Kind.FILE,
            lesson__status=Lesson.Status.PUBLISHED,
        )
        if not resource.file:
            return error_response("MATERIAL_NOT_AVAILABLE", "This learning file is not available.", status.HTTP_404_NOT_FOUND)
        try:
            file_handle = resource.file.open("rb")
        except FileNotFoundError:
            return error_response("MATERIAL_NOT_AVAILABLE", "This learning file is not available.", status.HTTP_404_NOT_FOUND)

        response = FileResponse(
            file_handle,
            as_attachment=False,
            filename=resource.original_filename or resource.file.name,
            content_type=resource.content_type or "application/octet-stream",
        )
        response["X-Content-Type-Options"] = "nosniff"
        return response


class QuizSubmitView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "quiz"

    @transaction.atomic
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, lesson_id=lesson_id, status=Lesson.Status.PUBLISHED)
        serializer = QuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answers = {str(k): str(v) for k, v in serializer.validated_data["answers"].items()}
        questions = list(lesson.questions.prefetch_related("options"))
        if not questions:
            return error_response("QUIZ_NOT_AVAILABLE", "This lesson does not have a quiz yet.", status.HTTP_409_CONFLICT)
        question_ids = {str(question.question_id) for question in questions}
        if set(answers.keys()) != question_ids:
            return error_response("INVALID_QUIZ_ANSWERS", "Answer every question in this lesson.", status.HTTP_400_BAD_REQUEST)
        correct = 0
        per_question = []
        for question in questions:
            selected = answers[str(question.question_id)]
            options = list(question.options.all())
            correct_options = [option for option in options if option.is_correct]
            if len(options) < 2 or len(correct_options) != 1:
                return error_response("QUIZ_NOT_AVAILABLE", "This lesson quiz is being updated. Try again later.", status.HTTP_409_CONFLICT)
            option_ids = {str(option.option_id) for option in options}
            if selected not in option_ids:
                return error_response("INVALID_QUIZ_ANSWERS", "One answer does not belong to this lesson.", status.HTTP_400_BAD_REQUEST)
            correct_option = correct_options[0]
            is_correct = str(correct_option.option_id) == selected
            correct += 1 if is_correct else 0
            per_question.append(
                {
                    "question_id": str(question.question_id),
                    "correct": is_correct,
                    "correct_option_id": str(correct_option.option_id),
                    "explanation": question.explanation,
                }
            )
        score = Decimal(correct * 100) / Decimal(len(questions) or 1)
        attempt = QuizAttempt.objects.create(
            user=request.user,
            lesson=lesson,
            score=score,
            answers=answers,
            duration_seconds=serializer.validated_data.get("duration_seconds"),
        )
        progress = progress_payload(request.user)
        return Response({"score": score, "per_question": per_question, "progress": progress, "attempt_id": attempt.attempt_id})


def progress_payload(user):
    published = Lesson.objects.filter(status=Lesson.Status.PUBLISHED)
    best_scores = QuizAttempt.objects.filter(user=user, lesson__in=published).values("lesson_id").annotate(best_score=Max("score"), attempts=Count("attempt_id"))
    best_by_lesson = {item["lesson_id"]: item for item in best_scores}
    completed = sum(1 for item in best_by_lesson.values() if item["best_score"] >= Decimal("70"))
    total = published.count()
    categories = QuizAttempt.objects.filter(user=user, lesson__status=Lesson.Status.PUBLISHED).values("lesson__category").annotate(average_score=Avg("score"))
    return {
        "lessons_total": total,
        "lessons_completed": completed,
        "completion_percent": round((completed / total) * 100, 2) if total else 0,
        "per_lesson": list(best_scores),
        "per_category": list(categories),
    }


class ProgressView(APIView):
    def get(self, request):
        return Response(progress_payload(request.user))


class AdminLessonListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        return Response(AdminLessonSerializer(lessons_with_quiz_data(), many=True).data)

    def post(self, request):
        serializer = AdminLessonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lesson = serializer.save(created_by=request.user)
        audit(request.user, "lesson.create", lesson)
        return Response(AdminLessonSerializer(lesson).data, status=status.HTTP_201_CREATED)


class AdminStarterModuleView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        existing_lessons = {
            lesson.template_key: lesson
            for lesson in Lesson.objects.filter(template_key__in=[module["key"] for module in STARTER_MODULES]).annotate(
                question_count=Count("questions")
            )
        }
        return Response(
            {
                "modules": [
                    {
                        "key": module["key"],
                        "title": module["title"],
                        "category": module["category"],
                        "summary": module["summary"],
                        "lesson_id": getattr(existing_lessons.get(module["key"]), "lesson_id", None),
                        "status": getattr(existing_lessons.get(module["key"]), "status", None),
                        "question_count": getattr(existing_lessons.get(module["key"]), "question_count", 0),
                    }
                    for module in STARTER_MODULES
                ]
            }
        )

    @transaction.atomic
    def post(self, request):
        key = request.data.get("key")
        module = STARTER_MODULES_BY_KEY.get(key) if isinstance(key, str) else None
        if module is None:
            return error_response("INVALID_MODULE_TEMPLATE", "Choose one of the available learning modules.", status.HTTP_400_BAD_REQUEST)

        lesson, created = Lesson.objects.get_or_create(
            template_key=key,
            defaults={
                "title": module["title"],
                "category": module["category"],
                "body": module["body"],
                "order_index": module["order_index"],
                "created_by": request.user,
            },
        )
        if created:
            for index, (prompt, correct_answer, incorrect_answers, explanation) in enumerate(module["questions"]):
                question = QuizQuestion.objects.create(
                    lesson=lesson,
                    prompt=prompt,
                    explanation=explanation,
                    order_index=index,
                )
                QuizOption.objects.bulk_create(
                    [
                        QuizOption(question=question, text=correct_answer, is_correct=True),
                        *[QuizOption(question=question, text=answer, is_correct=False) for answer in incorrect_answers],
                    ]
                )
            audit(request.user, "lesson.create_starter_module", lesson)

        lesson = lessons_with_quiz_data().get(lesson_id=lesson.lesson_id)
        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response({"lesson": AdminLessonSerializer(lesson).data, "created": created}, status=response_status)


class AdminLessonDetailView(APIView):
    permission_classes = [IsAdminRole]

    def get_object(self, lesson_id):
        return get_object_or_404(lessons_with_quiz_data(), lesson_id=lesson_id)

    def get(self, request, lesson_id):
        return Response(AdminLessonSerializer(self.get_object(lesson_id)).data)

    def patch(self, request, lesson_id):
        lesson = self.get_object(lesson_id)
        serializer = AdminLessonSerializer(lesson, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        audit(request.user, "lesson.update", lesson)
        return Response(AdminLessonSerializer(lesson).data)

    def delete(self, request, lesson_id):
        lesson = self.get_object(lesson_id)
        audit(request.user, "lesson.delete", lesson)
        lesson.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminLessonMaterialView(APIView):
    permission_classes = [IsAdminRole]

    def get_editable_lesson(self, lesson_id):
        lesson = get_object_or_404(Lesson, lesson_id=lesson_id)
        if lesson.status == Lesson.Status.PUBLISHED:
            return None
        return lesson

    def published_lesson_error(self):
        return error_response(
            "LESSON_IS_PUBLISHED",
            "Archive this lesson before changing its materials.",
            status.HTTP_409_CONFLICT,
        )

    def post(self, request, lesson_id):
        lesson = self.get_editable_lesson(lesson_id)
        if lesson is None:
            return self.published_lesson_error()

        serializer = AdminLessonResourceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resource = serializer.save(lesson=lesson)
        audit(request.user, "lesson_resource.create", resource)
        return Response(LessonResourceSerializer(resource).data, status=status.HTTP_201_CREATED)

    def delete(self, request, lesson_id):
        lesson = self.get_editable_lesson(lesson_id)
        if lesson is None:
            return self.published_lesson_error()

        resource = get_object_or_404(
            LessonResource,
            lesson_id=lesson.lesson_id,
            resource_id=request.data.get("resource_id") or request.query_params.get("resource_id"),
        )
        audit(request.user, "lesson_resource.delete", resource)
        if resource.file:
            resource.file.delete(save=False)
        resource.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminPublishLessonView(APIView):
    permission_classes = [IsAdminRole]

    @transaction.atomic
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson.objects.select_for_update(), lesson_id=lesson_id)
        questions = lesson.questions.annotate(
            option_count=Count("options"),
            correct_option_count=Count("options", filter=Q(options__is_correct=True)),
        )
        if not questions.exists():
            return error_response("LESSON_HAS_NO_QUESTIONS", "A lesson needs at least one question before publishing.", status.HTTP_400_BAD_REQUEST)
        if questions.filter(Q(option_count__lt=2) | ~Q(correct_option_count=1)).exists():
            return error_response(
                "LESSON_HAS_INVALID_QUESTIONS",
                "Every question needs at least two options and exactly one correct answer.",
                status.HTTP_400_BAD_REQUEST,
            )
        lesson.status = Lesson.Status.PUBLISHED
        lesson.save(update_fields=["status", "updated_at"])
        audit(request.user, "lesson.publish", lesson)
        return Response(AdminLessonSerializer(lesson).data)


class AdminArchiveLessonView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, lesson_id=lesson_id)
        lesson.status = Lesson.Status.ARCHIVED
        lesson.save(update_fields=["status", "updated_at"])
        audit(request.user, "lesson.archive", lesson)
        return Response(AdminLessonSerializer(lesson).data)


class AdminQuestionView(APIView):
    permission_classes = [IsAdminRole]

    def get_editable_lesson(self, lesson_id):
        lesson = get_object_or_404(Lesson, lesson_id=lesson_id)
        if lesson.status == Lesson.Status.PUBLISHED:
            return None
        return lesson

    def published_lesson_error(self):
        return error_response(
            "LESSON_IS_PUBLISHED",
            "Archive this lesson before changing its quiz.",
            status.HTTP_409_CONFLICT,
        )

    def post(self, request, lesson_id):
        lesson = self.get_editable_lesson(lesson_id)
        if lesson is None:
            return self.published_lesson_error()
        serializer = AdminQuizQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save(lesson=lesson)
        audit(request.user, "quiz_question.create", question)
        return Response(AdminQuizQuestionSerializer(question).data, status=status.HTTP_201_CREATED)

    def patch(self, request, lesson_id):
        lesson = self.get_editable_lesson(lesson_id)
        if lesson is None:
            return self.published_lesson_error()
        question = get_object_or_404(QuizQuestion, question_id=request.data.get("question_id"), lesson_id=lesson_id)
        serializer = AdminQuizQuestionSerializer(question, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        question = serializer.save()
        audit(request.user, "quiz_question.update", question)
        return Response(AdminQuizQuestionSerializer(question).data)

    def delete(self, request, lesson_id):
        lesson = self.get_editable_lesson(lesson_id)
        if lesson is None:
            return self.published_lesson_error()
        question = get_object_or_404(QuizQuestion, question_id=request.data.get("question_id"), lesson_id=lesson_id)
        audit(request.user, "quiz_question.delete", question)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminStatusView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        return Response(
            {
                "lessons": list(Lesson.objects.values("status").annotate(count=Count("lesson_id"))),
                "quiz_questions": QuizQuestion.objects.count(),
                "quiz_options": QuizOption.objects.count(),
            }
        )

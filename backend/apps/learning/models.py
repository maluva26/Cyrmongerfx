import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Lesson(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        ARCHIVED = "ARCHIVED", "Archived"

    lesson_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    template_key = models.CharField(max_length=80, null=True, blank=True, unique=True)
    category = models.CharField(max_length=80)
    body = models.TextField()
    illustration_refs = models.JSONField(default=list)
    order_index = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lesson"
        ordering = ["order_index", "title"]
        indexes = [models.Index(fields=["status", "order_index"])]


class QuizQuestion(models.Model):
    question_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="questions")
    prompt = models.TextField()
    explanation = models.TextField()
    order_index = models.IntegerField(default=0)

    class Meta:
        db_table = "quiz_question"
        ordering = ["order_index"]


class QuizOption(models.Model):
    option_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name="options")
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = "quiz_option"


class LessonResource(models.Model):
    class Kind(models.TextChoices):
        VIDEO = "VIDEO", "YouTube video"
        LINK = "LINK", "External link"
        FILE = "FILE", "Learning file"

    resource_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="resources")
    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=12, choices=Kind.choices)
    url = models.URLField(max_length=500, blank=True)
    file = models.FileField(upload_to="learning_materials/%Y/%m", blank=True)
    original_filename = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=127, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)
    order_index = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lesson_resource"
        ordering = ["order_index", "created_at"]
        indexes = [models.Index(fields=["lesson", "order_index"])]


class QuizAttempt(models.Model):
    attempt_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_attempts")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="attempts")
    score = models.DecimalField(max_digits=5, decimal_places=2)
    answers = models.JSONField(default=dict)
    completed_at = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = "quiz_attempt"
        ordering = ["-completed_at"]
        indexes = [models.Index(fields=["user", "lesson", "-completed_at"])]


def validate_question_options(question: QuizQuestion) -> None:
    options = list(question.options.all())
    if len(options) < 2:
        raise ValidationError("Each question must have at least two options.")
    if sum(1 for option in options if option.is_correct) != 1:
        raise ValidationError("Each question must have exactly one correct option.")

import re
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from django.db import transaction
from django.utils.text import get_valid_filename
from rest_framework import serializers

from .models import Lesson, LessonResource, QuizAttempt, QuizOption, QuizQuestion


ALLOWED_LEARNING_FILE_TYPES = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".csv": "text/csv",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
YOUTUBE_VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


def normalise_https_url(value):
    url = value.strip()
    try:
        parsed = urlsplit(url)
    except ValueError as exc:
        raise serializers.ValidationError("Enter a valid HTTPS URL.") from exc
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise serializers.ValidationError("Enter a valid HTTPS URL.")
    return parsed


def youtube_video_id(value):
    parsed = normalise_https_url(value)
    host = parsed.hostname.lower().rstrip(".")
    path_parts = [part for part in parsed.path.split("/") if part]
    video_id = None

    if host == "youtu.be" and path_parts:
        video_id = path_parts[0]
    elif host in {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif len(path_parts) >= 2 and path_parts[0] in {"embed", "shorts", "live"}:
            video_id = path_parts[1]

    if not isinstance(video_id, str) or not YOUTUBE_VIDEO_ID_PATTERN.fullmatch(video_id):
        raise serializers.ValidationError("Enter a valid YouTube video link.")
    return video_id


class LessonResourceSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()
    youtube_embed_url = serializers.SerializerMethodField()

    class Meta:
        model = LessonResource
        fields = [
            "resource_id",
            "title",
            "kind",
            "url",
            "original_filename",
            "content_type",
            "size_bytes",
            "order_index",
            "download_url",
            "youtube_embed_url",
        ]

    def get_download_url(self, obj):
        if obj.kind != LessonResource.Kind.FILE:
            return None
        return f"/lessons/{obj.lesson_id}/materials/{obj.resource_id}/download"

    def get_youtube_embed_url(self, obj):
        if obj.kind != LessonResource.Kind.VIDEO:
            return None
        video_id = parse_qs(urlsplit(obj.url).query).get("v", [None])[0]
        if not isinstance(video_id, str) or not YOUTUBE_VIDEO_ID_PATTERN.fullmatch(video_id):
            return None
        return f"https://www.youtube-nocookie.com/embed/{video_id}"


class AdminLessonResourceCreateSerializer(serializers.ModelSerializer):
    url = serializers.CharField(required=False, allow_blank=True, max_length=500)
    file = serializers.FileField(required=False, write_only=True, allow_empty_file=False)
    order_index = serializers.IntegerField(required=False, min_value=0)

    class Meta:
        model = LessonResource
        fields = ["title", "kind", "url", "file", "order_index"]

    def validate(self, attrs):
        kind = attrs["kind"]
        url = attrs.get("url", "")
        uploaded_file = attrs.get("file")

        if kind == LessonResource.Kind.VIDEO:
            if uploaded_file:
                raise serializers.ValidationError({"file": "YouTube videos must use a link, not a file upload."})
            if not url:
                raise serializers.ValidationError({"url": "Add a YouTube video link."})
            video_id = youtube_video_id(url)
            attrs["url"] = f"https://www.youtube.com/watch?v={video_id}"
        elif kind == LessonResource.Kind.LINK:
            if uploaded_file:
                raise serializers.ValidationError({"file": "External learning links cannot include a file upload."})
            if not url:
                raise serializers.ValidationError({"url": "Add an HTTPS learning link."})
            normalise_https_url(url)
            attrs["url"] = url.strip()
        elif kind == LessonResource.Kind.FILE:
            if url:
                raise serializers.ValidationError({"url": "Upload a file instead of adding a link."})
            if not uploaded_file:
                raise serializers.ValidationError({"file": "Choose a learning file to upload."})

            filename = get_valid_filename(Path(uploaded_file.name).name)
            extension = Path(filename).suffix.lower()
            if not filename or extension not in ALLOWED_LEARNING_FILE_TYPES:
                allowed = ", ".join(sorted(ALLOWED_LEARNING_FILE_TYPES))
                raise serializers.ValidationError({"file": f"Allowed file types: {allowed}."})

            max_size = 10 * 1024 * 1024
            if uploaded_file.size > max_size:
                raise serializers.ValidationError({"file": "Files must be 10 MB or smaller."})

            uploaded_file.name = filename
            attrs["original_filename"] = filename
            attrs["content_type"] = ALLOWED_LEARNING_FILE_TYPES[extension]
            attrs["size_bytes"] = uploaded_file.size
            attrs["url"] = ""

        return attrs

    def create(self, validated_data):
        uploaded_file = validated_data.pop("file", None)
        return LessonResource.objects.create(file=uploaded_file, **validated_data)


class LessonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["lesson_id", "title", "category", "order_index", "status", "updated_at"]


class QuizOptionPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizOption
        fields = ["option_id", "text"]


class StarterModuleQuestionImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_alt = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        from .starter_modules import STARTER_MODULES_BY_KEY

        module = STARTER_MODULES_BY_KEY.get(obj.lesson.template_key)
        return module["image_url"] if module else None

    def get_image_alt(self, obj):
        from .starter_modules import STARTER_MODULES_BY_KEY

        module = STARTER_MODULES_BY_KEY.get(obj.lesson.template_key)
        return module["image_alt"] if module else None

    class Meta:
        model = QuizQuestion
        fields = ["image_url", "image_alt"]


class QuizQuestionPublicSerializer(StarterModuleQuestionImageSerializer):
    options = QuizOptionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = QuizQuestion
        fields = ["question_id", "prompt", "order_index", "options", "image_url", "image_alt"]


class LessonDetailSerializer(serializers.ModelSerializer):
    questions = QuizQuestionPublicSerializer(many=True, read_only=True)
    resources = LessonResourceSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = ["lesson_id", "title", "category", "body", "illustration_refs", "order_index", "status", "resources", "questions"]


class QuizSubmitSerializer(serializers.Serializer):
    answers = serializers.DictField(child=serializers.UUIDField())
    duration_seconds = serializers.IntegerField(required=False, min_value=0)


class AdminQuizOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizOption
        fields = ["option_id", "text", "is_correct"]


class AdminQuizQuestionSerializer(StarterModuleQuestionImageSerializer):
    options = AdminQuizOptionSerializer(many=True)

    class Meta:
        model = QuizQuestion
        fields = ["question_id", "prompt", "explanation", "order_index", "options", "image_url", "image_alt"]

    def validate_options(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Add at least two options.")
        if sum(1 for item in value if item.get("is_correct")) != 1:
            raise serializers.ValidationError("Select exactly one correct option.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        options = validated_data.pop("options")
        question = QuizQuestion.objects.create(**validated_data)
        QuizOption.objects.bulk_create([QuizOption(question=question, **option) for option in options])
        return question

    @transaction.atomic
    def update(self, instance, validated_data):
        options = validated_data.pop("options", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if options is not None:
            instance.options.all().delete()
            QuizOption.objects.bulk_create([QuizOption(question=instance, **option) for option in options])
        return instance


class AdminLessonSerializer(serializers.ModelSerializer):
    questions = AdminQuizQuestionSerializer(many=True, read_only=True)
    resources = LessonResourceSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "lesson_id",
            "title",
            "template_key",
            "category",
            "body",
            "illustration_refs",
            "order_index",
            "status",
            "resources",
            "questions",
        ]
        read_only_fields = ["status", "template_key"]


class QuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = ["attempt_id", "lesson_id", "score", "answers", "completed_at", "duration_seconds"]

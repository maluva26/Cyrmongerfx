from django.conf import settings
from rest_framework import serializers

from .models import CommunityMessage


class CommunityMessageSerializer(serializers.ModelSerializer):
    author_id = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    is_demo = serializers.SerializerMethodField()

    class Meta:
        model = CommunityMessage
        fields = ["message_id", "author_id", "author_name", "body", "image_url", "is_demo", "created_at"]

    def get_author_id(self, obj):
        return str(obj.user_id) if obj.user_id else None

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url

    def get_is_demo(self, obj):
        return obj.user_id is None


class CommunityMessageCreateSerializer(serializers.ModelSerializer):
    body = serializers.CharField(required=False, allow_blank=True, max_length=1000, trim_whitespace=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CommunityMessage
        fields = ["body", "image"]

    def validate_image(self, value):
        if not value:
            return value
        max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
        if value.size > max_bytes:
            raise serializers.ValidationError(f"Image must be {settings.MAX_UPLOAD_MB} MB or smaller.")
        if value.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise serializers.ValidationError("Only PNG, JPEG and WebP images are supported.")
        return value

    def validate(self, attrs):
        body = attrs.get("body", "")
        image = attrs.get("image")
        if not body.strip() and not image:
            raise serializers.ValidationError("Write a message or attach an image.")
        return attrs

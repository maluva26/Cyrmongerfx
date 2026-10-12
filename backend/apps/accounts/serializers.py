from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_id", "email", "full_name", "role", "status", "email_verified_at", "must_change_password"]
        read_only_fields = ["user_id", "email", "role", "status", "email_verified_at", "must_change_password"]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    full_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    accepted_terms = serializers.BooleanField()
    terms_version = serializers.CharField(max_length=20, default="draft-2026-10")

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_accepted_terms(self, value):
        if not value:
            raise serializers.ValidationError("You must accept the terms, privacy policy and risk disclosure.")
        return value

    def validate_email(self, value):
        email = User.objects.normalize_email(value)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email

    def create(self, validated_data):
        accepted_terms = validated_data.pop("accepted_terms")
        terms_version = validated_data.pop("terms_version")
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            full_name=validated_data.get("full_name", ""),
            terms_accepted_at=timezone.now() if accepted_terms else None,
            terms_version=terms_version,
        )
        if not settings.EMAIL_VERIFICATION_REQUIRED:
            user.email_verified_at = timezone.now()
            user.save(update_fields=["email_verified_at"])
        return user


class AdminAccountCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    full_name = serializers.CharField(max_length=120, required=False, allow_blank=True)

    def validate_email(self, value):
        email = User.objects.normalize_email(value)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            full_name=validated_data.get("full_name", ""),
            role=User.Role.ADMIN,
            email_verified_at=timezone.now(),
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    admin_only = serializers.BooleanField(required=False, default=False, write_only=True)


class MeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["full_name"]


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value, user=self.context["request"].user)
        return value


class DeleteAccountSerializer(serializers.Serializer):
    confirmation = serializers.CharField()

    def validate_confirmation(self, value):
        if value != "DELETE":
            raise serializers.ValidationError("Type DELETE to confirm account deletion.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

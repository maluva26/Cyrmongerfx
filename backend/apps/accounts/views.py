from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import audit
from apps.core.permissions import IsAdminRole
from apps.core.responses import error_response

from .models import User
from .serializers import (
    AdminAccountCreateSerializer,
    DeleteAccountSerializer,
    LoginSerializer,
    MeUpdateSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserSerializer,
)


GENERIC_AUTH_FAILURE = "Invalid email or password"


def _client_ip(request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _set_refresh_cookie(response: Response, refresh: RefreshToken) -> None:
    response.set_cookie(
        settings.REFRESH_COOKIE_NAME,
        str(refresh),
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        path=settings.REFRESH_COOKIE_PATH,
        max_age=7 * 24 * 60 * 60,
    )


def _token_pair(user: User) -> tuple[str, "RefreshToken"]:
    refresh: "RefreshToken" = RefreshToken.for_user(user)  # type: ignore[assignment]
    return str(refresh.access_token), refresh


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        audit(user, "auth.register", user, _client_ip(request))
        return Response({"user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)


class AdminAccountCreateView(APIView):
    permission_classes = [IsAdminRole]

    @transaction.atomic
    def post(self, request):
        serializer = AdminAccountCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        audit(request.user, "auth.admin_account.create", user, _client_ip(request))
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = User.objects.normalize_email(serializer.validated_data["email"])
        password = serializer.validated_data["password"]
        admin_only = serializer.validated_data.get("admin_only", False)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return error_response("INVALID_CREDENTIALS", GENERIC_AUTH_FAILURE, status.HTTP_401_UNAUTHORIZED)

        if user.locked_until and user.locked_until > timezone.now():
            return error_response(
                "ACCOUNT_TEMPORARILY_LOCKED",
                "Too many failed attempts. Please try again later.",
                status.HTTP_429_TOO_MANY_REQUESTS,
            )
        if user.status != User.Status.ACTIVE or not user.check_password(password):
            locked = user.lock_for_failures()
            code = "ACCOUNT_TEMPORARILY_LOCKED" if locked else "INVALID_CREDENTIALS"
            http_status = status.HTTP_429_TOO_MANY_REQUESTS if locked else status.HTTP_401_UNAUTHORIZED
            message = "Too many failed attempts. Please try again later." if locked else GENERIC_AUTH_FAILURE
            return error_response(code, message, http_status)
        expected_role = User.Role.ADMIN if admin_only else User.Role.TRADER
        if user.role != expected_role:
            if user.role == User.Role.ADMIN:
                return error_response(
                    "ADMIN_LOGIN_REQUIRED",
                    "Administrator accounts must use the admin sign-in page.",
                    status.HTTP_403_FORBIDDEN,
                )
            return error_response(
                "TRADER_LOGIN_REQUIRED",
                "Trader accounts must use the normal sign-in page.",
                status.HTTP_403_FORBIDDEN,
            )

        user.reset_login_failures()
        access, refresh = _token_pair(user)
        audit(user, "auth.login", user, _client_ip(request))
        response = Response({"access": access, "user": UserSerializer(user).data})
        _set_refresh_cookie(response, refresh)
        return response


class RefreshView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        token = request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
        if not token:
            return error_response("REFRESH_REQUIRED", "Please sign in again.", status.HTTP_401_UNAUTHORIZED)
        try:
            old_refresh = RefreshToken(token)
            user = User.objects.get(pk=old_refresh["user_id"], status=User.Status.ACTIVE)
            old_refresh.blacklist()
        except Exception:
            return error_response("INVALID_REFRESH", "Please sign in again.", status.HTTP_401_UNAUTHORIZED)
        access, refresh = _token_pair(user)
        response = Response({"access": access, "user": UserSerializer(user).data})
        _set_refresh_cookie(response, refresh)
        return response


class LogoutView(APIView):
    def post(self, request):
        token = request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
        if token:
            try:
                RefreshToken(token).blacklist()
            except Exception:
                pass
        audit(request.user, "auth.logout", request.user, _client_ip(request))
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(settings.REFRESH_COOKIE_NAME, path=settings.REFRESH_COOKIE_PATH)
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = MeUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)

    @transaction.atomic
    def delete(self, request):
        serializer = DeleteAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        audit(request.user, "account.delete", request.user, _client_ip(request))
        request.user.delete()
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(settings.REFRESH_COOKIE_NAME, path=settings.REFRESH_COOKIE_PATH)
        return response


class PasswordChangeView(APIView):
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.validated_data["current_password"]):
            return error_response("INVALID_CURRENT_PASSWORD", "Current password is incorrect.", status.HTTP_400_BAD_REQUEST)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.must_change_password = False
        request.user.save(update_fields=["password", "must_change_password", "updated_at"])
        audit(request.user, "auth.password_change", request.user, _client_ip(request))
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = User.objects.normalize_email(serializer.validated_data["email"])
        user = User.objects.filter(email=email, status=User.Status.ACTIVE).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            send_mail(
                "Reset your Cyrmonger Algo Fx password",
                f"Use this reset token in the app. uid={uid} token={token}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        return Response({"message": "If that email exists, password reset instructions have been sent."})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data["uid"]))
            user = User.objects.get(pk=uid, status=User.Status.ACTIVE)
        except Exception:
            return error_response("INVALID_RESET_TOKEN", "Password reset link is invalid or expired.", status.HTTP_400_BAD_REQUEST)
        if not default_token_generator.check_token(user, serializer.validated_data["token"]):
            return error_response("INVALID_RESET_TOKEN", "Password reset link is invalid or expired.", status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password", "updated_at"])
        audit(user, "auth.password_reset", user, _client_ip(request))
        return Response(status=status.HTTP_204_NO_CONTENT)

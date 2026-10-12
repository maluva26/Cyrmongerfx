from django.urls import path

from .views import (
    AdminAccountCreateView,
    LoginView,
    LogoutView,
    MeView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RefreshView,
    RegisterView,
)

urlpatterns = [
    path("auth/register", RegisterView.as_view(), name="register"),
    path("auth/admin-accounts", AdminAccountCreateView.as_view(), name="admin-account-create"),
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/refresh", RefreshView.as_view(), name="refresh"),
    path("auth/logout", LogoutView.as_view(), name="logout"),
    path("auth/password/change", PasswordChangeView.as_view(), name="password-change"),
    path("auth/password/reset-request", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("auth/password/reset-confirm", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("me", MeView.as_view(), name="me"),
]

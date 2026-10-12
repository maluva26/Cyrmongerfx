from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

required = {
    "DJANGO_SECRET_KEY": SECRET_KEY,  # noqa: F405
    "DATABASE_URL": env("DATABASE_URL", default=""),  # noqa: F405
    "DJANGO_ALLOWED_HOSTS": ",".join(ALLOWED_HOSTS),  # noqa: F405
}
for name, value in required.items():
    if not value or value == "dev-only-change-me":
        raise ImproperlyConfigured(f"{name} must be set in production")

if INFERENCE_BACKEND == "mock" and not ALLOW_DEMO_MODEL:  # noqa: F405
    raise ImproperlyConfigured("Refusing to start production with mock inference unless ALLOW_DEMO_MODEL=True.")

from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parents[2]
env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    FREE_TIER_MODE=(bool, True),
    ALLOW_DEMO_MODEL=(bool, False),
    EMAIL_VERIFICATION_REQUIRED=(bool, False),
    MARKET_DATA_ENABLED=(bool, True),
    ASSISTANT_ENABLED=(bool, True),
    MAX_UPLOAD_MB=(int, 2),
    SIGNED_URL_TTL_SECONDS=(int, 300),
    CHART_RETENTION_DAYS=(int, 7),
    MIN_CONFIDENCE_THRESHOLD=(float, 0.50),
    DISPLAY_CONFIDENCE_THRESHOLD=(float, 0.60),
    ASSISTANT_MAX_TOKENS=(int, 700),
    MARKET_CACHE_SECONDS=(int, 300),
    MAX_RISK_PERCENT=(int, 5),
)

env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-only-change-me")
DEBUG = env("DJANGO_DEBUG")
FREE_TIER_MODE = env("FREE_TIER_MODE")
ALLOW_DEMO_MODEL = env("ALLOW_DEMO_MODEL")

ALLOWED_HOSTS = [host.strip() for host in env("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",") if host.strip()]
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in env("CORS_ALLOWED_ORIGINS", default="http://localhost:3000").split(",") if origin.strip()]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in env("CSRF_TRUSTED_ORIGINS", default="http://localhost:3000").split(",") if origin.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "django_filters",
    "apps.core",
    "apps.accounts",
    "apps.inference",
    "apps.charts",
    "apps.learning",
    "apps.risk",
    "apps.journal",
    "apps.assistant",
    "apps.market",
    "apps.reports",
    "apps.feedback",
    "apps.community",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

database_url = env("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
DATABASES = {"default": env.db_url("DATABASE_URL", default=database_url)}
if DATABASES["default"]["ENGINE"].endswith("postgresql"):
    DATABASES["default"].setdefault("OPTIONS", {})
    DATABASES["default"]["OPTIONS"]["sslmode"] = "require"

AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardPageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.core.exceptions.custom_exception_handler",
    # The report exporter uses ?format=csv|pdf as a normal query parameter.
    # DRF would otherwise treat it as a renderer override and 404 the request.
    "URL_FORMAT_OVERRIDE": None,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
        "auth": env("AUTH_RATE_LIMIT", default="5/min"),
        "analyze": env("ANALYZE_RATE_LIMIT", default="30/hour"),
        "assistant": env("ASSISTANT_RATE_LIMIT", default="15/day"),
        "quiz": env("QUIZ_RATE_LIMIT", default="60/hour"),
        "feedback": "20/day",
        "internal": "30/day",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "USER_ID_FIELD": "user_id",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Cyrmonger Algo Fx Educational API",
    "DESCRIPTION": "Educational Forex chart analysis and learning API. No broker/order execution.",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SAMESITE = "Strict"

REFRESH_COOKIE_NAME = "refresh"
REFRESH_COOKIE_PATH = "/api/v1/auth"
REFRESH_COOKIE_SECURE = not DEBUG
REFRESH_COOKIE_SAMESITE = "Strict"

SUPABASE_URL = env("SUPABASE_URL", default="")
SUPABASE_SERVICE_ROLE_KEY = env("SUPABASE_SERVICE_ROLE_KEY", default="")
SUPABASE_STORAGE_BUCKET = env("SUPABASE_STORAGE_BUCKET", default="chart-uploads")
SIGNED_URL_TTL_SECONDS = env("SIGNED_URL_TTL_SECONDS")

MAX_UPLOAD_MB = env("MAX_UPLOAD_MB")
ALLOWED_IMAGE_TYPES = [item.strip() for item in env("ALLOWED_IMAGE_TYPES", default="image/png,image/jpeg,image/webp").split(",")]
CHART_RETENTION_DAYS = env("CHART_RETENTION_DAYS")

INFERENCE_BACKEND = env("INFERENCE_BACKEND", default="mock")
INFERENCE_SERVICE_URL = env("INFERENCE_SERVICE_URL", default="")
INFERENCE_SERVICE_TOKEN = env("INFERENCE_SERVICE_TOKEN", default="")
MODEL_PATH = env("MODEL_PATH", default="ml/weights/model.pt")
MODEL_VERSION = env("MODEL_VERSION", default="mock-0.1")
MIN_CONFIDENCE_THRESHOLD = env("MIN_CONFIDENCE_THRESHOLD")
DISPLAY_CONFIDENCE_THRESHOLD = env("DISPLAY_CONFIDENCE_THRESHOLD")

LLM_PROVIDER = env("LLM_PROVIDER", default="gemini")
LLM_MODEL = env("LLM_MODEL", default="")
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY", default="")
GEMINI_API_KEY = env("GEMINI_API_KEY", default="")
ASSISTANT_MAX_TOKENS = env("ASSISTANT_MAX_TOKENS")
ASSISTANT_ENABLED = env("ASSISTANT_ENABLED")

MARKET_DATA_ENABLED = env("MARKET_DATA_ENABLED")
TWELVE_DATA_API_KEY = env("TWELVE_DATA_API_KEY", default="")
MARKET_CACHE_SECONDS = env("MARKET_CACHE_SECONDS")
MAX_RISK_PERCENT = env("MAX_RISK_PERCENT")

EMAIL_VERIFICATION_REQUIRED = env("EMAIL_VERIFICATION_REQUIRED")
DEFAULT_FROM_EMAIL = env("EMAIL_FROM", default="onboarding@resend.dev")
INTERNAL_CRON_TOKEN = env("INTERNAL_CRON_TOKEN", default="")
SENTRY_DSN = env("SENTRY_DSN", default="")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
        "plain": {"format": "%(levelname)s %(name)s %(message)s"},
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "plain"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

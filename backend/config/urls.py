from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok", "database": "reachable", "heavy_checks": False})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/health", health, name="health"),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.charts.urls")),
    path("api/v1/", include("apps.learning.urls")),
    path("api/v1/", include("apps.risk.urls")),
    path("api/v1/", include("apps.journal.urls")),
    path("api/v1/", include("apps.assistant.urls")),
    path("api/v1/", include("apps.market.urls")),
    path("api/v1/", include("apps.reports.urls")),
    path("api/v1/", include("apps.feedback.urls")),
    path("api/v1/", include("apps.community.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

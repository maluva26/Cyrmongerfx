from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class StorageUnavailable(RuntimeError):
    pass


class SupabaseChartStorage:
    def __init__(self) -> None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise StorageUnavailable("Supabase Storage is not configured.")
        from supabase import create_client

        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        self.bucket = settings.SUPABASE_STORAGE_BUCKET

    def upload(self, path: str, data: bytes, mime_type: str) -> str:
        self.client.storage.from_(self.bucket).upload(
            path,
            data,
            {"content-type": mime_type, "x-upsert": "false"},
        )
        return path

    def signed_url(self, path: str) -> str:
        result = self.client.storage.from_(self.bucket).create_signed_url(path, settings.SIGNED_URL_TTL_SECONDS)
        return result.get("signedURL") or result.get("signedUrl")

    def delete(self, path: str) -> None:
        self.client.storage.from_(self.bucket).remove([path])


class LocalDevChartStorage:
    def upload(self, path: str, data: bytes, mime_type: str) -> str:
        default_storage.save(path, ContentFile(data))
        return path

    def signed_url(self, path: str) -> str:
        return settings.MEDIA_URL + path.replace("\\", "/")

    def delete(self, path: str) -> None:
        if default_storage.exists(path):
            default_storage.delete(path)


def get_chart_storage():
    try:
        return SupabaseChartStorage()
    except StorageUnavailable:
        if settings.DEBUG:
            Path(settings.MEDIA_ROOT).mkdir(parents=True, exist_ok=True)
            return LocalDevChartStorage()
        raise

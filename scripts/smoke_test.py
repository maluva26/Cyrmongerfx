"""Smoke test: register -> login -> analyze -> quiz -> risk -> logout -> delete."""
import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
django.setup()

from django.test import Client  # noqa: E402


def run():
    c = Client()
    email = "smoke@example.com"
    password = "SmokeTest123!"
    # register
    r = c.post("/api/v1/auth/register", {"email": email, "password": password, "accepted_terms": True, "terms_version": "draft-2026-10"}, content_type="application/json")
    assert r.status_code == 201, f"register failed: {r.content}"
    # login
    r = c.post("/api/v1/auth/login", {"email": email, "password": password}, content_type="application/json")
    assert r.status_code == 200, f"login failed: {r.content}"
    access = r.json()["access"]
    auth = {"HTTP_AUTHORIZATION": f"Bearer {access}"}
    # analyze (1x1 PNG)
    import io  # noqa: E401
    from PIL import Image  # noqa: E401
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), "white").save(buf, "PNG")
    buf.seek(0)
    r = c.post("/api/v1/charts/analyze", {"image": buf}, **auth)
    assert r.status_code in (201, 503), f"analyze failed: {r.content}"
    # quiz (draft lesson returns 404)
    from apps.learning.models import Lesson  # noqa: E402
    lesson = Lesson.objects.filter(status=Lesson.Status.PUBLISHED).first()
    if lesson:
        r = c.post(f"/api/v1/lessons/{lesson.lesson_id}/quiz", {"answers": {}}, content_type="application/json", **auth)
        assert r.status_code == 400
    # risk calc
    r = c.post("/api/v1/risk/calculate", {"account_balance": 1000, "risk_percent": 1, "entry_price": 1.1, "stop_loss": 1.0}, content_type="application/json", **auth)
    assert r.status_code == 200, f"risk failed: {r.content}"
    # logout
    r = c.post("/api/v1/auth/logout", content_type="application/json", **auth)
    assert r.status_code == 204
    # delete account
    r = c.post("/api/v1/auth/login", {"email": email, "password": password}, content_type="application/json")
    access = r.json()["access"]
    auth = {"HTTP_AUTHORIZATION": f"Bearer {access}"}
    r = c.delete("/api/v1/me", {"confirmation": "DELETE"}, content_type="application/json", **auth)
    assert r.status_code == 204, f"delete failed: {r.content}"
    print("Smoke test passed.")


if __name__ == "__main__":
    run()

"""Measure analyze endpoint latency."""
import io
import os
import statistics
import sys
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import django  # noqa: E402
django.setup()

from django.test import Client  # noqa: E402
from PIL import Image  # noqa: E402


def main(n=10):
    c = Client()
    # create user and login once
    import json  # noqa: E401
    email = "latency@example.com"
    password = "LatencyTest123!"
    r = c.post("/api/v1/auth/register", {"email": email, "password": password, "accepted_terms": True, "terms_version": "draft-2026-10"}, content_type="application/json")
    r = c.post("/api/v1/auth/login", {"email": email, "password": password}, content_type="application/json")
    access = r.json()["access"]
    auth = {"HTTP_AUTHORIZATION": f"Bearer {access}"}
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), "white").save(buf, "PNG")
    buf.seek(0)
    times = []
    for _ in range(n):
        start = time.perf_counter()
        c.post("/api/v1/charts/analyze", {"image": buf}, **auth)
        times.append(time.perf_counter() - start)
        buf.seek(0)
    print(f"n={n} mean={statistics.mean(times):.3f}s p95={sorted(times)[int(n*0.95)]:.3f}s")


if __name__ == "__main__":
    main()

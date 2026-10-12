import hashlib
from dataclasses import dataclass
from typing import Protocol, TypedDict

import httpx
from django.conf import settings

from .constants import ALLOWED_PATTERNS


class Detection(TypedDict):
    label: str
    confidence: float
    box: tuple[float, float, float, float]


class BaseDetector(Protocol):
    version: str

    def predict(self, image_bytes: bytes) -> list[Detection]: ...


class ModelUnavailable(RuntimeError):
    pass


@dataclass
class MockDetector:
    version: str = "mock-0.1"

    def predict(self, image_bytes: bytes) -> list[Detection]:
        digest = hashlib.sha256(image_bytes).digest()
        if digest[0] % 7 == 0:
            return []
        label = ALLOWED_PATTERNS[digest[1] % len(ALLOWED_PATTERNS)]
        confidence = 0.50 + (digest[2] / 255) * 0.45
        x_min = 0.08 + (digest[3] / 255) * 0.25
        y_min = 0.10 + (digest[4] / 255) * 0.25
        width = 0.35 + (digest[5] / 255) * 0.20
        height = 0.25 + (digest[6] / 255) * 0.20
        return [
            {
                "label": label,
                "confidence": round(confidence, 4),
                "box": (
                    round(x_min, 6),
                    round(y_min, 6),
                    round(min(x_min + width, 0.95), 6),
                    round(min(y_min + height, 0.95), 6),
                ),
            }
        ]


class RemoteDetector:
    def __init__(self) -> None:
        self.version = settings.MODEL_VERSION or "remote"
        self.url = settings.INFERENCE_SERVICE_URL.rstrip("/")
        self.token = settings.INFERENCE_SERVICE_TOKEN
        if not self.url or not self.token:
            raise ModelUnavailable("Inference service is not configured.")

    def predict(self, image_bytes: bytes) -> list[Detection]:
        try:
            response = httpx.post(
                f"{self.url}/predict",
                headers={"X-Inference-Token": self.token},
                files={"image": ("chart.png", image_bytes, "application/octet-stream")},
                timeout=15,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            raise ModelUnavailable("The model service is unavailable. It may be waking up; please retry in a minute.") from exc
        self.version = payload.get("model_version", self.version)
        return payload.get("detections", [])


def get_active_detector() -> BaseDetector:
    backend = settings.INFERENCE_BACKEND.lower()
    if backend == "mock":
        return MockDetector(version=settings.MODEL_VERSION or "mock-0.1")
    if backend in {"remote", "service"}:
        return RemoteDetector()
    raise ModelUnavailable(f"Inference backend '{backend}' is not available in the Django API process.")

import hashlib
import os
from typing import List

import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from PIL import Image, ImageOps
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="Cyrmonger Algo Fx Inference Service")

API_TOKEN = os.getenv("INFERENCE_SERVICE_TOKEN", "")
X_INFERENCE_TOKEN = APIKeyHeader(name="X-Inference-Token", auto_error=False)

ALLOWED_PATTERNS = [
    "head_and_shoulders",
    "inverse_head_and_shoulders",
    "double_top",
    "double_bottom",
    "ascending_triangle",
    "descending_triangle",
    "order_block_bullish",
    "order_block_bearish",
    "fair_value_gap_bullish",
    "fair_value_gap_bearish",
]


class Detection(BaseModel):
    label: str
    confidence: float
    box: List[float]


class PredictResponse(BaseModel):
    model_version: str
    detections: List[Detection]


def _auth(header: str):
    if not API_TOKEN or header != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid inference token.")


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": False}


@app.post("/predict", response_model=PredictResponse)
async def predict(file: bytes = ..., authorization: str = Security(X_INFERENCE_TOKEN)):
    _auth(authorization)
    digest = hashlib.sha256(file).digest()
    if digest[0] % 7 == 0:
        return PredictResponse(model_version="mock-0.1", detections=[])
    label = ALLOWED_PATTERNS[digest[1] % len(ALLOWED_PATTERNS)]
    confidence = 0.50 + (digest[2] / 255) * 0.45
    x_min = 0.08 + (digest[3] / 255) * 0.25
    y_min = 0.10 + (digest[4] / 255) * 0.25
    width = 0.35 + (digest[5] / 255) * 0.20
    height = 0.25 + (digest[6] / 255) * 0.20
    box = [
        round(x_min, 6),
        round(y_min, 6),
        round(min(x_min + width, 0.95), 6),
        round(min(y_min + height, 0.95), 6),
    ]
    return PredictResponse(
        model_version="mock-0.1",
        detections=[Detection(label=label, confidence=round(confidence, 4), box=box)],
    )

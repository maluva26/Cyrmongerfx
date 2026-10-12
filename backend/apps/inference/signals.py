from django.conf import settings

from .constants import BEARISH_PATTERNS, BULLISH_PATTERNS


def generate_signal(detections: list[dict]) -> tuple[str, float | None]:
    if not detections:
        return "NEUTRAL", None
    bullish = sum(d["confidence"] for d in detections if d["label"] in BULLISH_PATTERNS)
    bearish = sum(d["confidence"] for d in detections if d["label"] in BEARISH_PATTERNS)
    top_confidence = max(float(d["confidence"]) for d in detections)
    if top_confidence < settings.MIN_CONFIDENCE_THRESHOLD:
        return "NEUTRAL", round(top_confidence, 4)
    if bullish and bearish and abs(bullish - bearish) < 0.15:
        return "NEUTRAL", round(top_confidence, 4)
    if bullish > bearish:
        return "BUY", round(top_confidence, 4)
    if bearish > bullish:
        return "SELL", round(top_confidence, 4)
    return "NEUTRAL", round(top_confidence, 4)

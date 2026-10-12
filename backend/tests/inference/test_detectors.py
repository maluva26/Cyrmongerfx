from apps.charts.views import _valid_box
from apps.inference.constants import ALLOWED_PATTERNS
from apps.inference.detectors import MockDetector, get_active_detector
from apps.inference.signals import generate_signal


class TestInference:
    def test_mock_detector(self, settings):
        settings.INFERENCE_BACKEND = "mock"
        settings.MODEL_VERSION = "mock-0.1"
        det = get_active_detector()
        assert isinstance(det, MockDetector)
        res = det.predict(b"abc")
        assert isinstance(res, list)

    def test_signal_bullish(self):
        signal, _ = generate_signal([{"label": "inverse_head_and_shoulders", "confidence": 0.9}])
        assert signal == "BUY"

    def test_signal_bearish(self):
        signal, _ = generate_signal([{"label": "head_and_shoulders", "confidence": 0.9}])
        assert signal == "SELL"

    def test_signal_neutral_conflict(self):
        signal, _ = generate_signal(
            [
                {"label": "inverse_head_and_shoulders", "confidence": 0.9},
                {"label": "head_and_shoulders", "confidence": 0.9},
            ]
        )
        assert signal == "NEUTRAL"

    def test_signal_resolves_conflict_beyond_margin(self):
        signal, _ = generate_signal(
            [
                {"label": "inverse_head_and_shoulders", "confidence": 0.95},
                {"label": "head_and_shoulders", "confidence": 0.60},
            ]
        )
        assert signal == "BUY"

    def test_signal_neutral_when_below_threshold(self, settings):
        settings.MIN_CONFIDENCE_THRESHOLD = 0.80
        signal, confidence = generate_signal([{"label": "double_top", "confidence": 0.55}])
        assert signal == "NEUTRAL"
        assert confidence == 0.55

    def test_signal_empty_is_neutral(self):
        signal, confidence = generate_signal([])
        assert signal == "NEUTRAL"
        assert confidence is None

    def test_mock_detector_is_deterministic(self, settings):
        settings.INFERENCE_BACKEND = "mock"
        detector = get_active_detector()
        assert detector.predict(b"same-bytes") == detector.predict(b"same-bytes")

    def test_mock_detector_only_emits_valid_detections(self, settings):
        settings.INFERENCE_BACKEND = "mock"
        detector = get_active_detector()
        payloads = [b"a", b"bb", b"ccc", b"dddd", b"eeeee", b"ffffff", b"ggggggg", b"hhhhhhhh", b"iiiiiiiii"]
        seen = 0
        for payload in payloads:
            for detection in detector.predict(payload):
                seen += 1
                assert detection["label"] in ALLOWED_PATTERNS
                assert 0.0 <= float(detection["confidence"]) <= 1.0
                assert _valid_box(detection["box"]) is True
        assert seen > 0

    def test_valid_box_helper(self):
        assert _valid_box([0.1, 0.2, 0.6, 0.7]) is True
        assert _valid_box([0.0, 0.0, 1.0, 1.0]) is True
        assert _valid_box([0.6, 0.2, 0.1, 0.7]) is False
        assert _valid_box([0.1, 0.2, 0.6]) is False
        assert _valid_box("nope") is False
        assert _valid_box([1.2, 0.0, 1.5, 0.5]) is False

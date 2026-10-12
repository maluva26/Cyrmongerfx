PATTERN_EXPLANATIONS = {
    "head_and_shoulders": "A head and shoulders pattern can show that upward momentum is weakening.",
    "inverse_head_and_shoulders": "An inverse head and shoulders pattern can show that downward momentum is weakening.",
    "double_top": "A double top can show price struggling to break above the same area twice.",
    "double_bottom": "A double bottom can show price rejecting the same lower area twice.",
    "ascending_triangle": "An ascending triangle can show buyers pressing against resistance.",
    "descending_triangle": "A descending triangle can show sellers pressing against support.",
    "order_block_bullish": "A bullish order block marks an area where buyers may have previously stepped in.",
    "order_block_bearish": "A bearish order block marks an area where sellers may have previously stepped in.",
    "fair_value_gap_bullish": "A bullish fair value gap marks a fast move upward that may later attract attention.",
    "fair_value_gap_bearish": "A bearish fair value gap marks a fast move downward that may later attract attention.",
}


def create_educational_explanation(detections: list[dict]) -> str:
    if not detections:
        return "No supported chart pattern was detected with enough confidence. Try a clearer chart image."
    parts = []
    for detection in detections:
        label = detection["label"]
        confidence = float(detection["confidence"])
        text = PATTERN_EXPLANATIONS.get(label, "This pattern needs careful confirmation with price context.")
        parts.append(f"{label.replace('_', ' ').title()}: {text} Model score: {confidence:.2f}.")
    parts.append("Use this as a learning aid together with your own analysis and risk management.")
    return " ".join(parts)

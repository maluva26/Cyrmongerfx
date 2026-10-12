# Model Training Guide

## Dataset Layout

```
data/
  train/
    images/*.png
    labels/*.json
  val/
    images/*.png
    labels/*.json
  test/
    images/*.png
    labels/*.json
```

### Label Format (JSON per image)
```json
{
  "image": "001.png",
  "width": 1280,
  "height": 720,
  "annotations": [
    {"label": "head_and_shoulders", "confidence": 1.0, "box": [0.1, 0.2, 0.5, 0.6]}
  ]
}
```

### Classes (must match ALLOWED_PATTERNS in inference/constants.py)
1. head_and_shoulders
2. inverse_head_and_shoulders
3. double_top
4. double_bottom
5. ascending_triangle
6. descending_triangle
7. order_block_bullish
8. order_block_bearish
9. fair_value_gap_bullish
10. fair_value_gap_bearish

### Splitting
- Split by chart/time, not random crops. Each chart belongs to exactly one split.
- No leakage between train/val/test.

### Annotation Tool
Use LabelImg or Roboflow. Export bounding boxes in normalised coordinates [x_min, y_min, x_max, y_max] where values are 0..1 relative to image dimensions.

## Training

```bash
python backend/ml/train.py --data-dir data --arch resnet18 --epochs 20 --batch-size 16
```

Outputs:
- `backend/ml/weights/model.pt`
- `backend/ml/weights/model_card.json`

## Evaluation

```bash
python backend/ml/evaluate.py --weights backend/ml/weights/model.pt --data-dir data/test
```

Prints per-class precision, recall, F1 and a confusion matrix PNG. Checks the >=80% accuracy release gate.

## Important Notes
- The mock detector is for development only.
- Real accuracy claims require a real labelled, held-out dataset.
- No horizontal flips in augmentation because they swap bullish/bearish meaning.
- Free-tier mode keeps the backend API process light; inference runs via a separate service.

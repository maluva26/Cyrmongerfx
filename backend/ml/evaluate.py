"""Evaluate a trained chart pattern model."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms


def build_transforms():
    return transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )


def build_model(arch: str, num_classes: int):
    if arch == "resnet18":
        model = models.resnet18()
        model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
    elif arch == "vgg16":
        model = models.vgg16()
        model.classifier[6] = torch.nn.Linear(model.classifier[6].in_features, num_classes)
    else:
        raise ValueError(f"Unsupported arch: {arch}")
    return model


def evaluate(args):
    data_dir = Path(args.data_dir)
    test_ds = datasets.ImageFolder(data_dir, transform=build_transforms())
    loader = DataLoader(test_ds, batch_size=32, num_workers=2)
    classes = test_ds.classes
    num_classes = len(classes)

    model = build_model(args.arch, num_classes)
    state = torch.load(args.weights, map_location="cpu")
    model.load_state_dict(state)
    model.eval()

    all_preds = []
    all_targets = []
    with torch.no_grad():
        for imgs, targets in loader:
            outputs = model(imgs)
            preds = outputs.argmax(dim=1)
            all_preds.extend(preds.numpy())
            all_targets.extend(targets.numpy())

    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)
    accuracy = (all_preds == all_targets).mean()

    # Per-class precision/recall/F1
    cm = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(all_targets, all_preds):
        cm[t, p] += 1

    print(f"Accuracy: {accuracy:.4f}")
    print("Per-class metrics:")
    for i, cls in enumerate(classes):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        print(f"  {cls}: P={prec:.3f} R={rec:.3f} F1={f1:.3f}")

    # Confusion matrix PNG
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.colorbar(im, ax=ax)
    tick_marks = np.arange(num_classes)
    ax.set_xticks(tick_marks, classes, rotation=45, ha="right")
    ax.set_yticks(tick_marks, classes)
    thresh = cm.max() / 2.0
    for i in range(num_classes):
        for j in range(num_classes):
            ax.text(j, i, format(cm[i, j], "d"), ha="center", va="center", color="white" if cm[i, j] > thresh else "black")
    ax.set_ylabel("True")
    ax.set_xlabel("Predicted")
    plt.tight_layout()
    out = Path("ml/weights/confusion_matrix.png")
    plt.savefig(out)
    print(f"Confusion matrix saved to {out}")

    gate_met = accuracy >= 0.80
    print(f"Release gate (>=0.80 accuracy): {'PASS' if gate_met else 'FAIL'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", type=str, required=True)
    parser.add_argument("--data-dir", type=str, required=True)
    parser.add_argument("--arch", type=str, default="resnet18")
    evaluate(parser.parse_args())

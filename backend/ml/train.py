"""Train a chart pattern classifier using transfer learning."""

import argparse
import json
import random
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms


def build_transforms():
    return transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )


def train(args):
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    data_dir = Path(args.data_dir)
    train_ds = datasets.ImageFolder(data_dir / "train", transform=build_transforms())
    val_ds = datasets.ImageFolder(data_dir / "val", transform=build_transforms())
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, num_workers=2)
    num_classes = len(train_ds.classes)

    arch = args.arch.lower()
    if arch == "resnet18":
        model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    elif arch == "vgg16":
        model = models.vgg16(weights=models.VGG16_Weights.DEFAULT)
    else:
        raise ValueError(f"Unsupported arch: {arch}")

    # Replace head
    if arch.startswith("resnet"):
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    elif arch.startswith("vgg"):
        model.classifier[6] = nn.Linear(model.classifier[6].in_features, num_classes)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

    best_acc = 0.0
    weights_dir = Path("ml/weights")
    weights_dir.mkdir(parents=True, exist_ok=True)

    for epoch in range(args.epochs):
        model.train()
        for imgs, targets in train_loader:
            imgs, targets = imgs.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(imgs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
        # Validation
        model.eval()
        correct = total = 0
        with torch.no_grad():
            for imgs, targets in val_loader:
                imgs, targets = imgs.to(device), targets.to(device)
                outputs = model(imgs)
                preds = outputs.argmax(dim=1)
                correct += (preds == targets).sum().item()
                total += targets.size(0)
        acc = correct / total if total else 0.0
        print(f"Epoch {epoch+1}/{args.epochs} val_acc={acc:.4f}")
        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), weights_dir / "model.pt")
            model_card = {
                "version": f"{arch}-{epoch+1}",
                "architecture": arch,
                "classes": train_ds.classes,
                "val_accuracy": best_acc,
                "epochs": epoch + 1,
            }
            (weights_dir / "model_card.json").write_text(json.dumps(model_card, indent=2))

    print(f"Best val accuracy: {best_acc:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=str, required=True)
    parser.add_argument("--arch", type=str, default="resnet18")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    train(parser.parse_args())

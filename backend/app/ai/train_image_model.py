"""Fine-tune a phishing image classifier from folder-labeled images.

Expected layout:
    phishing_dataset/legitimate/*.png
    phishing_dataset/phishing/*.png

Run with:
    .venv\\Scripts\\python.exe -m backend.app.ai.train_image_model
"""
import argparse
import json
import random
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, Subset, WeightedRandomSampler
from torchvision import datasets, models
from torchvision.models import ResNet18_Weights

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def split_indices(targets, seed=42):
    random.seed(seed)
    by_class = {}
    for index, target in enumerate(targets):
        by_class.setdefault(target, []).append(index)

    train, validation, test = [], [], []
    for indices in by_class.values():
        random.shuffle(indices)
        train_end = int(len(indices) * 0.7)
        validation_end = train_end + int(len(indices) * 0.15)
        train.extend(indices[:train_end])
        validation.extend(indices[train_end:validation_end])
        test.extend(indices[validation_end:])
    return train, validation, test


def train(dataset_dir: Path, output_path: Path, epochs: int, batch_size: int):
    if not (dataset_dir / "legitimate").is_dir() or not (dataset_dir / "phishing").is_dir():
        raise SystemExit(
            "Dataset chưa đủ. Cần cả hai thư mục phishing_dataset/legitimate và phishing_dataset/phishing."
        )

    weights = ResNet18_Weights.DEFAULT
    base_dataset = datasets.ImageFolder(dataset_dir)
    if set(base_dataset.classes) != {"legitimate", "phishing"}:
        raise SystemExit(f"Nhãn không đúng: {base_dataset.classes}. Cần legitimate và phishing.")
    if min(base_dataset.targets.count(label) for label in range(len(base_dataset.classes))) < 2:
        raise SystemExit("Mỗi lớp cần ít nhất 2 ảnh để chia train/validation/test.")

    train_indices, validation_indices, test_indices = split_indices(base_dataset.targets)
    train_dataset = Subset(datasets.ImageFolder(dataset_dir, transform=weights.transforms()), train_indices)
    validation_dataset = Subset(datasets.ImageFolder(dataset_dir, transform=weights.transforms()), validation_indices)
    test_dataset = Subset(datasets.ImageFolder(dataset_dir, transform=weights.transforms()), test_indices)

    train_targets = [base_dataset.targets[index] for index in train_indices]
    class_counts = torch.bincount(torch.tensor(train_targets), minlength=len(base_dataset.classes)).float()
    sample_weights = [1.0 / class_counts[target] for target in train_targets]
    sampler = WeightedRandomSampler(sample_weights, len(sample_weights), replacement=True)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, sampler=sampler, num_workers=0)
    validation_loader = DataLoader(validation_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    model = models.resnet18(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, len(base_dataset.classes))
    for parameter in model.parameters():
        parameter.requires_grad = False
    for parameter in model.fc.parameters():
        parameter.requires_grad = True

    optimizer = torch.optim.AdamW(model.fc.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()
    best_validation_accuracy = -1.0

    for epoch in range(epochs):
        model.train()
        for images, labels in train_loader:
            optimizer.zero_grad()
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()

        validation_accuracy = evaluate(model, validation_loader)
        print(f"epoch {epoch + 1}/{epochs} validation_accuracy={validation_accuracy:.3f}")
        if validation_accuracy >= best_validation_accuracy:
            best_validation_accuracy = validation_accuracy
            output_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(
                {"model_state": model.state_dict(), "class_to_idx": base_dataset.class_to_idx},
                output_path,
            )

    model.load_state_dict(torch.load(output_path, map_location="cpu", weights_only=False)["model_state"])
    test_accuracy = evaluate(model, test_loader)
    print(f"test_accuracy={test_accuracy:.3f}")
    print(json.dumps({"classes": base_dataset.class_to_idx, "test_accuracy": test_accuracy}))


def evaluate(model, loader):
    model.eval()
    correct = total = 0
    with torch.inference_mode():
        for images, labels in loader:
            predictions = model(images).argmax(dim=1)
            correct += int((predictions == labels).sum())
            total += labels.numel()
    return correct / total if total else 0.0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("phishing_dataset"))
    parser.add_argument("--output", type=Path, default=Path("models/phishing_resnet18.pt"))
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    train(args.dataset, args.output, args.epochs, args.batch_size)

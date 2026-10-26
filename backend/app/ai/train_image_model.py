"""Train the image classifier with leakage-controlled, source-aware splits.

Recommended dataset layout:
    phishing_dataset/legitimate/*.png
    phishing_dataset/phishing/*.png
    phishing_dataset/manifest.csv

The manifest must contain:
    path,label,source,template_id,split

``source`` identifies where the image came from (public, synthetic, anonymized,
or a source name), while ``template_id`` groups variants of one design.  A
template/source group must never occur in more than one split.

Run with:
    .venv\\Scripts\\python.exe -m backend.app.ai.train_image_model ^
        --dataset phishing_dataset --manifest phishing_dataset/manifest.csv
"""
import argparse
import csv
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import torch
from PIL import Image
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, f1_score
from torch import nn
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
from torchvision import models, transforms
from torchvision.models import ResNet18_Weights

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
LABELS = {"legitimate", "phishing"}
SPLITS = {"train", "validation", "test"}


class ManifestImageDataset(Dataset):
    def __init__(self, records, class_to_idx, transform):
        self.records = records
        self.class_to_idx = class_to_idx
        self.transform = transform

    def __len__(self):
        return len(self.records)

    def __getitem__(self, index):
        record = self.records[index]
        with Image.open(record["path"]) as image:
            image = image.convert("RGB")
        return self.transform(image), self.class_to_idx[record["label"]]


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as image_file:
        for block in iter(lambda: image_file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest(dataset_dir, manifest_path):
    if not manifest_path.exists():
        raise SystemExit(
            f"Thiếu manifest {manifest_path}. Hãy tạo CSV có các cột "
            "path,label,source,template_id,split để tránh leakage giữa các tập."
        )

    records = []
    seen_hashes = {}
    with manifest_path.open("r", encoding="utf-8-sig", newline="") as file:
        for line_number, row in enumerate(csv.DictReader(file), start=2):
            required = {"path", "label", "source", "template_id", "split"}
            missing = required - set(row)
            if missing:
                raise SystemExit(f"Manifest dòng {line_number} thiếu cột: {sorted(missing)}")
            path = (dataset_dir / row["path"]).resolve()
            label = row["label"].strip().lower()
            split = row["split"].strip().lower()
            source = row["source"].strip()
            template_id = row["template_id"].strip()
            if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
                raise SystemExit(f"Ảnh không tồn tại hoặc không hỗ trợ ở dòng {line_number}: {path}")
            if label not in LABELS or split not in SPLITS or not source or not template_id:
                raise SystemExit(
                    f"Manifest dòng {line_number} cần label hợp lệ, source, template_id "
                    f"và split thuộc {sorted(SPLITS)}."
                )
            file_hash = _sha256(path)
            previous = seen_hashes.get(file_hash)
            if previous and previous["split"] != split:
                raise SystemExit(
                    f"Trùng nội dung giữa các tập: {path} và {previous['path']}. "
                    "Hãy giữ cùng một split hoặc loại bản sao."
                )
            seen_hashes[file_hash] = {"path": str(path), "split": split}
            records.append(
                {
                    "path": path,
                    "label": label,
                    "source": source,
                    "template_id": template_id,
                    "split": split,
                    "sha256": file_hash,
                }
            )

    if not records:
        raise SystemExit("Manifest không có ảnh.")

    source_splits = defaultdict(set)
    template_splits = defaultdict(set)
    for record in records:
        # A source and a template are split units, not individual images.
        source_splits[record["source"]].add(record["split"])
        template_splits[record["template_id"]].add(record["split"])
    leaking_sources = [source for source, splits in source_splits.items() if len(splits) > 1]
    leaking_templates = [
        template for template, splits in template_splits.items() if len(splits) > 1
    ]
    if leaking_sources or leaking_templates:
        raise SystemExit(
            "Một source hoặc template xuất hiện ở nhiều split. "
            f"Sources: {leaking_sources[:5]}; templates: {leaking_templates[:5]}. "
            "Mỗi source/template phải chỉ thuộc một split."
        )
    counts = Counter(record["split"] for record in records)
    for split in SPLITS:
        if not counts[split]:
            raise SystemExit(f"Split {split} đang rỗng.")
    return records


def _transforms():
    normalize = ResNet18_Weights.DEFAULT.transforms()
    # Augmentation is applied only to training records below.
    train_transform = transforms.Compose(
        [
            transforms.RandomResizedCrop(224, scale=(0.85, 1.0)),
            transforms.RandomRotation(5),
            transforms.ColorJitter(brightness=0.15, contrast=0.15),
            transforms.RandomApply([transforms.GaussianBlur(3, sigma=(0.1, 1.0))], p=0.15),
            transforms.ToTensor(),
            transforms.Normalize(mean=normalize.mean, std=normalize.std),
        ]
    )
    return train_transform, normalize


def _evaluate(model, loader):
    model.eval()
    labels, predictions = [], []
    with torch.inference_mode():
        for images, batch_labels in loader:
            outputs = model(images).argmax(dim=1)
            labels.extend(batch_labels.tolist())
            predictions.extend(outputs.tolist())
    if not labels:
        return {"macro_f1": 0.0, "balanced_accuracy": 0.0, "confusion_matrix": []}
    return {
        "macro_f1": float(f1_score(labels, predictions, average="macro", zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(labels, predictions)),
        "confusion_matrix": confusion_matrix(labels, predictions, labels=[0, 1]).tolist(),
    }


def train(dataset_dir: Path, manifest_path: Path, output_path: Path, epochs: int, batch_size: int, use_pretrained: bool = False):
    records = load_manifest(dataset_dir, manifest_path)
    class_to_idx = {"legitimate": 0, "phishing": 1}
    train_records = [record for record in records if record["split"] == "train"]
    validation_records = [record for record in records if record["split"] == "validation"]
    test_records = [record for record in records if record["split"] == "test"]
    train_transform, eval_transform = _transforms()

    train_dataset = ManifestImageDataset(train_records, class_to_idx, train_transform)
    validation_dataset = ManifestImageDataset(validation_records, class_to_idx, eval_transform)
    test_dataset = ManifestImageDataset(test_records, class_to_idx, eval_transform)
    train_targets = [class_to_idx[record["label"]] for record in train_records]
    class_counts = torch.bincount(torch.tensor(train_targets), minlength=2).float()
    if torch.any(class_counts == 0):
        raise SystemExit("Train phải có cả hai lớp legitimate và phishing.")
    sample_weights = [1.0 / class_counts[target] for target in train_targets]
    sampler = WeightedRandomSampler(sample_weights, len(sample_weights), replacement=True)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, sampler=sampler, num_workers=0)
    validation_loader = DataLoader(validation_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    weights = None
    if use_pretrained:
        try:
            weights = ResNet18_Weights.DEFAULT
            model = models.resnet18(weights=weights)
        except Exception:
            model = models.resnet18(weights=None)
    else:
        model = models.resnet18(weights=None)

    model.fc = nn.Linear(model.fc.in_features, 2)
    if weights is not None:
        for parameter in model.parameters():
            parameter.requires_grad = False
        for parameter in model.fc.parameters():
            parameter.requires_grad = True
        optimizer = torch.optim.AdamW(model.fc.parameters(), lr=1e-3)
    else:
        for parameter in model.parameters():
            parameter.requires_grad = True
        optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
    criterion = nn.CrossEntropyLoss()
    best_validation_f1 = -1.0
    output_path.parent.mkdir(parents=True, exist_ok=True)
    for epoch in range(epochs):
        model.train()
        for images, labels in train_loader:
            optimizer.zero_grad()
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()
        validation_metrics = _evaluate(model, validation_loader)
        print(
            f"epoch {epoch + 1}/{epochs} "
            f"validation_macro_f1={validation_metrics['macro_f1']:.3f}"
        )
        if validation_metrics["macro_f1"] >= best_validation_f1:
            best_validation_f1 = validation_metrics["macro_f1"]
            torch.save(
                {
                    "model_state": model.state_dict(),
                    "class_to_idx": class_to_idx,
                    "dataset_manifest": str(manifest_path),
                    "selection_metric": "validation_macro_f1",
                    "validation_metrics": validation_metrics,
                },
                output_path,
            )

    checkpoint = torch.load(output_path, map_location="cpu", weights_only=False)
    model.load_state_dict(checkpoint["model_state"])
    test_metrics = _evaluate(model, test_loader)
    summary = {
        "classes": class_to_idx,
        "counts": dict(Counter(record["split"] for record in records)),
        "test_metrics": test_metrics,
        "unseen_sources": sorted({record["source"] for record in test_records}),
        "unseen_templates": sorted({record["template_id"] for record in test_records}),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    output_path.with_suffix(".metrics.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("phishing_dataset"))
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=Path("models/phishing_resnet18.pt"))
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--pretrained", action="store_true", default=False)
    args = parser.parse_args()
    manifest = args.manifest or args.dataset / "manifest.csv"
    random.seed(42)
    torch.manual_seed(42)
    train(args.dataset, manifest, args.output, args.epochs, args.batch_size, use_pretrained=args.pretrained)

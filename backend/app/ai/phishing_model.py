"""Inference for the locally fine-tuned phishing image classifier."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PIL import Image

MODEL_PATH = Path("models/phishing_resnet18.pt")

_classifier = None


@dataclass
class PhishingImageResult:
    available: bool
    probability: float
    label: str
    explanation: str


def _load_classifier():
    global _classifier
    if _classifier is not None:
        return _classifier
    if not MODEL_PATH.exists():
        return None

    try:
        import torch
        from torchvision.models import ResNet18_Weights, resnet18

        checkpoint = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
        model = resnet18(weights=None)
        model.fc = torch.nn.Linear(model.fc.in_features, len(checkpoint["class_to_idx"]))
        model.load_state_dict(checkpoint["model_state"])
        model.eval()
        _classifier = (model, checkpoint["class_to_idx"], ResNet18_Weights.DEFAULT.transforms())
        return _classifier
    except Exception:
        return None


def analyze_phishing_image(image_path: str) -> PhishingImageResult:
    loaded = _load_classifier()
    if loaded is None:
        return PhishingImageResult(
            available=False,
            probability=0.0,
            label="unavailable",
            explanation="Chưa có model phishing đã train. Hệ thống dùng OCR và kiểm tra dấu hiệu ảnh hiện có.",
        )

    try:
        import torch

        model, class_to_idx, transform = loaded
        image = Image.open(image_path).convert("RGB")
        input_tensor = transform(image).unsqueeze(0)
        with torch.inference_mode():
            probabilities = torch.softmax(model(input_tensor), dim=1)[0]

        phishing_index = class_to_idx.get("phishing")
        if phishing_index is None:
            return PhishingImageResult(False, 0.0, "unavailable", "Model thiếu nhãn phishing.")

        probability = float(probabilities[phishing_index])
        label = "phishing" if probability >= 0.5 else "legitimate"
        explanation = (
            f"Model ảnh ước tính {probability * 100:.1f}% khả năng đây là ảnh phishing."
            if label == "phishing"
            else f"Model ảnh ước tính {(1 - probability) * 100:.1f}% khả năng đây là ảnh hợp lệ."
        )
        return PhishingImageResult(True, round(probability, 4), label, explanation)
    except Exception:
        return PhishingImageResult(
            False, 0.0, "unavailable", "Không thể chạy model ảnh; kết quả được trả từ các lớp phân tích khác."
        )

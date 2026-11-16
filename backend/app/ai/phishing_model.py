"""Inference for the locally fine-tuned phishing image classifier."""
from dataclasses import dataclass
from pathlib import Path
from threading import Lock

from PIL import Image, ImageStat

MODEL_PATH = Path("models/phishing_resnet18.pt")

_classifier = None
_classifier_load_error = ""
_inference_lock = Lock()


@dataclass
class PhishingImageResult:
    available: bool
    probability: float
    label: str
    explanation: str
    gradcam_available: bool = False
    gradcam_path: str = ""
    gradcam_target_class: str = ""
    gradcam_note: str = ""
    gradcam_focus_regions: list[str] | None = None


def _load_classifier():
    global _classifier, _classifier_load_error
    if _classifier is not None:
        return _classifier
    if not MODEL_PATH.exists():
        _classifier_load_error = f"Không tìm thấy checkpoint {MODEL_PATH}."
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
        _classifier_load_error = ""
        return _classifier
    except Exception as error:
        _classifier_load_error = f"{type(error).__name__}: {error}"
        return None


def _create_gradcam_explanation(
    model,
    input_tensor,
    image: Image.Image,
    target_index: int,
    target_label: str,
    image_path: str,
) -> tuple[bool, str, str, list[str]]:
    """Render the pixels that most increased the ResNet phishing-class score.

    Grad-CAM is an attribution map, not an object detector: a hot region means
    the classifier relied on that region, not that the region is independently
    proven to contain fraud.
    """
    try:
        import cv2
        import numpy as np
        from pytorch_grad_cam import GradCAM
        from pytorch_grad_cam.utils.image import show_cam_on_image
        from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

        target_layers = [model.layer4[-1]]
        model.zero_grad(set_to_none=True)
        with GradCAM(model=model, target_layers=target_layers) as cam:
            grayscale_cam = cam(
                input_tensor=input_tensor,
                targets=[ClassifierOutputTarget(target_index)],
                eigen_smooth=True,
            )[0]

        width, height = image.size
        resized_cam = cv2.resize(grayscale_cam, (width, height), interpolation=cv2.INTER_CUBIC)
        rgb_image = np.asarray(image, dtype=np.float32) / 255.0
        visualization = show_cam_on_image(rgb_image, resized_cam, use_rgb=True)

        # Summarize only the spatial location of the strongest CAM cells. This
        # is passed to the VLM as grounding context; it is deliberately not
        # turned into a semantic scam explanation here because CAM does not
        # know what the highlighted content means.
        row_names = ["phía trên", "ở giữa", "phía dưới"]
        column_names = ["bên trái", "ở giữa", "bên phải"]
        height_cam, width_cam = resized_cam.shape[:2]
        cells: list[tuple[float, str]] = []
        for row in range(3):
            for column in range(3):
                y0, y1 = row * height_cam // 3, (row + 1) * height_cam // 3
                x0, x1 = column * width_cam // 3, (column + 1) * width_cam // 3
                score = float(resized_cam[y0:y1, x0:x1].mean())
                location = f"{row_names[row]}, {column_names[column]}"
                cells.append((score, location))
        strongest = sorted(cells, reverse=True)[:2]
        focus_regions = [location for score, location in strongest if score >= 0.15]

        source_path = Path(image_path)
        output_path = source_path.with_name(f"{source_path.stem}.gradcam.jpg")
        Image.fromarray(visualization).save(output_path, format="JPEG", quality=92)
        return (
            True,
            str(output_path),
            f"Vùng đỏ/vàng đóng góp mạnh hơn vào dự đoán lớp {target_label} của ResNet18; "
            "bản đồ này giải thích sự chú ý của model, không tự chứng minh nội dung là lừa đảo.",
            focus_regions,
        )
    except (ImportError, OSError, RuntimeError, ValueError, AttributeError) as error:
        return False, "", f"Không thể tạo bản đồ Grad-CAM trong lần phân tích này: {error}", []


def analyze_phishing_image(image_path: str) -> PhishingImageResult:
    loaded = _load_classifier()
    if loaded is None:
        return PhishingImageResult(
            available=False,
            probability=0.0,
            label="unavailable",
            explanation="Chưa có model phishing đã train. Hệ thống dùng OCR và kiểm tra dấu hiệu ảnh hiện có.",
            gradcam_note=(
                "Không thể tạo Grad-CAM vì ResNet18 chưa nạp được. "
                f"Chi tiết: {_classifier_load_error or 'không xác định'}."
            ),
        )

    try:
        import torch

        model, class_to_idx, transform = loaded
        image = Image.open(image_path).convert("RGB")
        # A classifier trained on screenshots must not make a confident claim
        # about a blank scan, placeholder or single-colour photograph.  These
        # inputs carry no useful layout evidence and previously caused a strong
        # false positive because they are outside the training distribution.
        channel_variance = ImageStat.Stat(image.resize((128, 128))).var
        if max(channel_variance, default=0.0) < 2.0:
            return PhishingImageResult(
                available=False,
                probability=0.0,
                label="insufficient_visual_content",
                explanation="Ảnh gần như đồng màu nên không đủ chi tiết để model bố cục kết luận.",
                gradcam_note="Ảnh gần như đồng màu hoặc trang trống nên không đủ đặc trưng để tạo Grad-CAM.",
            )
        input_tensor = transform(image).unsqueeze(0)
        phishing_index = class_to_idx.get("phishing")
        if phishing_index is None:
            return PhishingImageResult(
                False,
                0.0,
                "unavailable",
                "Model thiếu nhãn phishing.",
                gradcam_note="Không thể tạo Grad-CAM vì checkpoint không có nhãn phishing.",
            )

        # A shared model must not have Grad-CAM hooks attached concurrently by
        # separate requests. Keep probability inference and attribution atomic.
        with _inference_lock:
            with torch.inference_mode():
                logits = model(input_tensor)
                # Temperature scaling (T=1.8) reduces extreme confidence values.
                probabilities = torch.softmax(logits / 1.8, dim=1)[0]
            probability = float(probabilities[phishing_index])
            label = "phishing" if probability >= 0.5 else "legitimate"
            target_index = class_to_idx.get(label)
            if target_index is None:
                return PhishingImageResult(
                    False,
                    0.0,
                    "unavailable",
                    f"Model thiếu nhãn {label}.",
                    gradcam_note=f"Không thể tạo Grad-CAM vì checkpoint không có nhãn {label}.",
                )
            gradcam_available, gradcam_path, gradcam_note, gradcam_focus_regions = _create_gradcam_explanation(
                model,
                input_tensor,
                image,
                target_index,
                label,
                image_path,
            )

        explanation = (
            f"Model ảnh ước tính {probability * 100:.1f}% khả năng đây là ảnh phishing."
            if label == "phishing"
            else f"Model ảnh ước tính {(1 - probability) * 100:.1f}% khả năng đây là ảnh hợp lệ."
        )
        return PhishingImageResult(
            True,
            round(probability, 4),
            label,
            explanation,
            gradcam_available=gradcam_available,
            gradcam_path=gradcam_path,
            gradcam_target_class=label,
            gradcam_note=gradcam_note,
            gradcam_focus_regions=gradcam_focus_regions,
        )
    except Exception as error:
        return PhishingImageResult(
            False,
            0.0,
            "unavailable",
            "Không thể chạy model ảnh; kết quả được trả từ các lớp phân tích khác.",
            gradcam_note=f"Không thể tạo Grad-CAM: {type(error).__name__}: {error}",
        )

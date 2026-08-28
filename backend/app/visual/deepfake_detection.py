"""
Deepfake / AI-generated image detection.

Có 2 chế độ:
  1. MODEL THẬT (khuyên dùng cho production): dùng model pretrained từ HuggingFace
     qua thư viện `transformers`. Cần tải model (~100-300MB) lúc chạy lần đầu,
     nên máy chạy phải có mạng ra ngoài internet.
  2. FALLBACK HEURISTIC (dùng khi không có mạng/model, hoặc để test nhanh):
     phân tích miền tần số (FFT) của ảnh. Deepfake/ảnh AI-generated thường để lại
     dấu vết bất thường ở miền tần số cao do quá trình upsampling của GAN/diffusion
     model. ĐÂY LÀ HEURISTIC THAM KHẢO, KHÔNG PHẢI BẰNG CHỨNG CHẮC CHẮN — độ chính
     xác thấp hơn nhiều so với model đã train, chỉ nên dùng làm tín hiệu phụ.

Cách bật model thật:
    pip install transformers torch
    (tự động tải model lần đầu chạy, cần mạng internet)
"""
from dataclasses import dataclass
from typing import Optional
import numpy as np
from PIL import Image

MODEL_ID = "prithivMLmods/deepfake-detector-model-v1"  # ví dụ model công khai trên HuggingFace
_pipeline_cache = None


@dataclass
class DeepfakeResult:
    is_likely_fake: bool
    confidence: float          # 0.0 - 1.0
    method: str                 # "model" hoặc "heuristic_fft"
    risk_contribution: int      # 0-30
    note: str


def _try_load_model_pipeline():
    """Lazy-load model thật, chỉ chạy khi được gọi lần đầu. Trả về None nếu không load được."""
    global _pipeline_cache
    if _pipeline_cache is not None:
        return _pipeline_cache
    try:
        from transformers import pipeline
        _pipeline_cache = pipeline("image-classification", model=MODEL_ID, framework="pt")
        return _pipeline_cache
    except Exception:
        # thiếu thư viện transformers/torch, hoặc không có mạng để tải model
        return None


def analyze_deepfake(image_path: str, force_heuristic: bool = False) -> DeepfakeResult:
    """
    Args:
        image_path: đường dẫn ảnh cần kiểm tra
        force_heuristic: True để bỏ qua model thật, luôn dùng fallback (dùng khi test/demo)
    """
    if not force_heuristic:
        model = _try_load_model_pipeline()
        if model is not None:
            return _analyze_with_model(image_path, model)

    return _analyze_with_fft_heuristic(image_path)


def _analyze_with_model(image_path: str, model) -> DeepfakeResult:
    image = Image.open(image_path).convert("RGB")
    predictions = model(image)  # list of {"label": ..., "score": ...}

    fake_score = 0.0
    for pred in predictions:
        label = pred["label"].lower()
        if "fake" in label or "deepfake" in label or "ai" in label or "generated" in label:
            fake_score = max(fake_score, pred["score"])

    is_fake = fake_score > 0.5
    risk = int(fake_score * 30) if is_fake else 0

    return DeepfakeResult(
        is_likely_fake=is_fake,
        confidence=round(fake_score, 3),
        method="model",
        risk_contribution=risk,
        note=(
            f"Model phát hiện {fake_score*100:.1f}% khả năng ảnh là deepfake/AI-generated."
            if is_fake
            else "Model không phát hiện dấu hiệu deepfake đáng kể."
        ),
    )


def _analyze_with_fft_heuristic(image_path: str) -> DeepfakeResult:
    """
    Fallback không cần model: phân tích năng lượng miền tần số cao bằng FFT.
    Ảnh AI-generated/deepfake thường có pattern lưới đều đặn ở tần số cao
    (artifact từ upsampling), khác với nhiễu tự nhiên của ảnh chụp camera thật.
    """
    image = Image.open(image_path).convert("L")  # chuyển grayscale để đơn giản hóa
    arr = np.array(image, dtype=np.float64)

    f_transform = np.fft.fft2(arr)
    f_shift = np.fft.fftshift(f_transform)
    magnitude = np.abs(f_shift)

    h, w = magnitude.shape
    center_h, center_w = h // 2, w // 2
    # vùng lõi trung tâm = tần số thấp, vùng rìa = tần số cao
    radius = min(h, w) // 4

    y, x = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((y - center_h) ** 2 + (x - center_w) ** 2)

    low_freq_mask = dist_from_center <= radius
    high_freq_mask = dist_from_center > radius

    low_energy = float(np.mean(magnitude[low_freq_mask]))
    high_energy = float(np.mean(magnitude[high_freq_mask]))

    # tỷ lệ năng lượng cao/thấp bất thường cao có thể là dấu hiệu artifact nhân tạo
    ratio = high_energy / max(low_energy, 1e-6)

    # ngưỡng này CHỈ MANG TÍNH THAM KHẢO, cần tinh chỉnh với dữ liệu thật
    is_suspicious = ratio > 0.15
    confidence = min(ratio / 0.3, 1.0) if is_suspicious else round(ratio / 0.15, 2)
    risk = int(confidence * 15) if is_suspicious else 0  # heuristic nên risk cap thấp hơn model thật

    return DeepfakeResult(
        is_likely_fake=is_suspicious,
        confidence=round(confidence, 3),
        method="heuristic_fft",
        risk_contribution=risk,
        note=(
            "[Heuristic - độ tin cậy thấp] Phát hiện pattern tần số cao bất thường, "
            "có thể là dấu hiệu ảnh qua xử lý AI. Khuyến nghị xác minh thêm bằng model chuyên dụng."
            if is_suspicious
            else "[Heuristic - độ tin cậy thấp] Không phát hiện pattern tần số bất thường rõ rệt."
        ),
    )

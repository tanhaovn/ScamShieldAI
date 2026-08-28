"""
Tổng hợp 3 kỹ thuật visual forensics (EXIF, ELA, deepfake detection) thành
1 kết quả visual risk duy nhất, có thể cộng thêm vào risk score từ text (OCR).

Trọng số dùng khi cộng dồn phản ánh độ tin cậy tương đối của từng kỹ thuật:
  - EXIF: tín hiệu khá đáng tin nếu có editing software rõ ràng -> giữ nguyên
  - ELA: đáng tin với ảnh JPEG có texture thật, cần ảnh thật để test kỹ -> giữ nguyên
  - Deepfake heuristic (fallback không model): ĐỘ TIN CẬY THẤP -> giảm trọng số 50%
    khi đang chạy ở method="heuristic_fft". Nếu dùng model thật (method="model")
    thì giữ nguyên trọng số.
"""
from dataclasses import dataclass, field
from typing import List

from backend.app.visual.exif_analysis import analyze_exif, ExifResult
from backend.app.visual.ela_analysis import analyze_ela, ElaResult
from backend.app.visual.deepfake_detection import analyze_deepfake, DeepfakeResult


@dataclass
class VisualRiskResult:
    visual_score: int  # 0-100, điểm rủi ro riêng từ phân tích hình ảnh
    flags: List[str] = field(default_factory=list)
    exif: ExifResult = None
    ela: ElaResult = None
    deepfake: DeepfakeResult = None


def analyze_image_visual(image_path: str, use_deepfake_model: bool = True) -> VisualRiskResult:
    """
    Chạy đầy đủ 3 bước visual forensics trên 1 ảnh.

    Args:
        image_path: đường dẫn ảnh
        use_deepfake_model: True để thử dùng model thật trước (fallback về heuristic
                             nếu model chưa cài/không có mạng); False để luôn dùng heuristic.
    """
    exif_result = analyze_exif(image_path)
    ela_result, _ela_image = analyze_ela(image_path)
    deepfake_result = analyze_deepfake(image_path, force_heuristic=not use_deepfake_model)

    flags: List[str] = []
    flags.extend(exif_result.flags)
    if ela_result.is_suspicious:
        flags.append(ela_result.note)
    if deepfake_result.is_likely_fake:
        flags.append(deepfake_result.note)

    deepfake_weight = 1.0 if deepfake_result.method == "model" else 0.5
    deepfake_contribution = int(deepfake_result.risk_contribution * deepfake_weight)

    total = exif_result.risk_contribution + ela_result.risk_contribution + deepfake_contribution
    visual_score = min(total, 100)

    return VisualRiskResult(
        visual_score=visual_score,
        flags=flags,
        exif=exif_result,
        ela=ela_result,
        deepfake=deepfake_result,
    )

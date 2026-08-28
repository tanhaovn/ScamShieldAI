"""
Error Level Analysis (ELA): kỹ thuật forensics kinh điển để phát hiện vùng
ảnh JPEG đã bị chỉnh sửa cục bộ (vd: dán số tiền giả vào hóa đơn thật,
sửa tên người nhận trong ảnh chuyển khoản).

Nguyên lý:
  1. Lưu lại ảnh gốc ở chất lượng JPEG cố định (vd 90%)
  2. So sánh pixel-by-pixel giữa ảnh gốc và ảnh vừa nén lại
  3. Vùng ảnh KHÔNG bị chỉnh sửa sẽ có mức chênh lệch nén đồng đều
  4. Vùng ảnh ĐÃ bị chỉnh sửa/dán đè thường có mức chênh lệch nén khác biệt
     rõ rệt so với phần còn lại (vì đã trải qua chu kỳ nén JPEG khác)

Hạn chế: chỉ hiệu quả với ảnh JPEG (không áp dụng tốt cho PNG gốc vì PNG
không nén mất dữ liệu). Ảnh đã qua nhiều lần re-save cũng làm giảm độ chính xác.
"""
import io
from dataclasses import dataclass
from typing import Tuple
from PIL import Image, ImageChops
import numpy as np

ELA_QUALITY = 90        # chất lượng JPEG dùng để nén lại khi so sánh
SUSPICIOUS_STD_THRESHOLD = 18.0   # ngưỡng độ lệch chuẩn để coi là bất thường
SUSPICIOUS_MAX_THRESHOLD = 90     # ngưỡng giá trị pixel chênh lệch tối đa


@dataclass
class ElaResult:
    mean_diff: float
    std_diff: float
    max_diff: int
    is_suspicious: bool
    risk_contribution: int  # 0-25
    note: str


def analyze_ela(image_path: str) -> Tuple[ElaResult, Image.Image]:
    """
    Chạy ELA trên ảnh, trả về kết quả phân tích + ảnh ELA (để hiển thị
    trực quan cho người dùng thấy vùng nào đáng ngờ - vùng sáng hơn = khác biệt nhiều hơn).
    """
    original = Image.open(image_path).convert("RGB")

    buffer = io.BytesIO()
    original.save(buffer, "JPEG", quality=ELA_QUALITY)
    buffer.seek(0)
    resaved = Image.open(buffer)

    ela_image = ImageChops.difference(original, resaved)
    ela_array = np.array(ela_image).astype(np.float64)

    mean_diff = float(np.mean(ela_array))
    std_diff = float(np.std(ela_array))
    max_diff = int(np.max(ela_array))

    is_suspicious = std_diff > SUSPICIOUS_STD_THRESHOLD or max_diff > SUSPICIOUS_MAX_THRESHOLD

    risk = 0
    if is_suspicious:
        # chênh lệch càng lớn, risk càng cao, cap ở 25
        risk = min(25, int((std_diff / SUSPICIOUS_STD_THRESHOLD) * 15))

    note = (
        f"Phát hiện vùng có mức nén không đồng đều (std={std_diff:.1f}, max={max_diff}) "
        f"— dấu hiệu có thể đã bị chỉnh sửa/dán đè cục bộ."
        if is_suspicious
        else f"Mức nén đồng đều trên toàn ảnh (std={std_diff:.1f}) — không phát hiện dấu hiệu dán đè rõ ràng."
    )

    # khuếch đại ảnh ELA để mắt người nhìn rõ hơn vùng khác biệt
    scale = 255.0 / max(ela_array.max(), 1)
    ela_visual = Image.fromarray((ela_array * scale).astype(np.uint8))

    result = ElaResult(
        mean_diff=round(mean_diff, 2),
        std_diff=round(std_diff, 2),
        max_diff=max_diff,
        is_suspicious=is_suspicious,
        risk_contribution=risk,
        note=note,
    )
    return result, ela_visual

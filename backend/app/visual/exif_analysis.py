"""
Phân tích EXIF metadata để tìm dấu hiệu ảnh đã bị chỉnh sửa bằng phần mềm.

Nguyên lý: ảnh chụp thẳng từ camera/điện thoại thường có EXIF đầy đủ
(hãng máy, model, ngày giờ chụp, GPS...). Ảnh đã qua Photoshop/GIMP/Canva
thường:
  - Có tag "Software" ghi tên phần mềm chỉnh sửa
  - Thiếu hoàn toàn EXIF (do re-export/re-save xóa mất metadata)
  - Ngày giờ chỉnh sửa (ModifyDate) khác ngày giờ chụp gốc (DateTimeOriginal)

Đây KHÔNG phải bằng chứng chắc chắn 100% (ảnh screenshot hợp lệ cũng
không có EXIF camera), nhưng là một tín hiệu hữu ích khi kết hợp với
các phân tích khác.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from PIL import Image
from PIL.ExifTags import TAGS

# Danh sách phần mềm chỉnh sửa ảnh phổ biến, nếu xuất hiện trong tag Software
# thì gần như chắc chắn ảnh đã qua chỉnh sửa thủ công
EDITING_SOFTWARE_SIGNATURES = [
    "photoshop", "gimp", "canva", "picsart", "lightroom",
    "snapseed", "pixlr", "affinity photo", "paint.net",
]


@dataclass
class ExifResult:
    has_exif: bool
    editing_software_detected: Optional[str] = None
    date_mismatch: bool = False
    flags: List[str] = field(default_factory=list)
    risk_contribution: int = 0  # điểm cộng vào risk score tổng (0-30)
    raw_exif: dict = field(default_factory=dict)


def analyze_exif(image_path: str) -> ExifResult:
    image = Image.open(image_path)
    exif_data = image.getexif()

    if not exif_data or len(exif_data) == 0:
        return ExifResult(
            has_exif=False,
            flags=["Ảnh không có metadata EXIF (có thể đã qua re-save/chỉnh sửa, hoặc là screenshot)"],
            risk_contribution=8,
        )

    readable_exif = {}
    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, tag_id)
        readable_exif[tag_name] = value

    flags = []
    risk = 0
    editing_software = None

    software_tag = str(readable_exif.get("Software", "")).lower()
    for sig in EDITING_SOFTWARE_SIGNATURES:
        if sig in software_tag:
            editing_software = readable_exif.get("Software")
            flags.append(f"Phát hiện ảnh đã qua phần mềm chỉnh sửa: '{editing_software}'")
            risk += 25
            break

    date_original = readable_exif.get("DateTimeOriginal")
    date_modified = readable_exif.get("DateTime")
    date_mismatch = False
    if date_original and date_modified and date_original != date_modified:
        date_mismatch = True
        flags.append(
            f"Ngày chụp gốc ({date_original}) khác ngày chỉnh sửa cuối ({date_modified})"
        )
        risk += 10

    if not flags:
        flags.append("EXIF có vẻ nguyên bản, không phát hiện dấu hiệu chỉnh sửa rõ ràng")

    return ExifResult(
        has_exif=True,
        editing_software_detected=editing_software,
        date_mismatch=date_mismatch,
        flags=flags,
        risk_contribution=min(risk, 30),
        raw_exif={k: str(v) for k, v in readable_exif.items()},
    )

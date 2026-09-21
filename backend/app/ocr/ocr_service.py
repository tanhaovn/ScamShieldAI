"""
Module OCR: trích văn bản tiếng Việt từ ảnh (hóa đơn, screenshot tin nhắn...).

Dùng pytesseract (wrapper của Tesseract OCR) vì dễ cài đặt.
Yêu cầu cài đặt hệ thống (Ubuntu/Debian):
    sudo apt-get install tesseract-ocr tesseract-ocr-vie

Nếu muốn độ chính xác cao hơn cho tiếng Việt, có thể thay bằng PaddleOCR
(pip install paddleocr paddlepaddle) — API tương tự, chỉ cần đổi hàm extract_text().
"""
import shutil
import subprocess
from pathlib import Path

from PIL import Image
import pytesseract


_local_tessdata = Path(__file__).resolve().parents[3] / "tessdata"
_tesseract_path = shutil.which("tesseract") or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if Path(_tesseract_path).exists():
    pytesseract.pytesseract.tesseract_cmd = _tesseract_path
_tessdata_config = (
    f"--tessdata-dir {_local_tessdata}"
    if (_local_tessdata / "vie.traineddata").exists()
    else ""
)


def extract_text(image_path: str) -> str:
    """
    Trích văn bản từ file ảnh.

    Args:
        image_path: đường dẫn tới file ảnh (jpg, png...)

    Returns:
        Chuỗi văn bản trích được (đã strip khoảng trắng thừa).
    """
    if not Path(_tesseract_path).exists():
        # Visual analysis can still run when the optional system OCR binary is absent.
        return ""

    # Gọi executable trực tiếp để tránh lỗi pytesseract tạo ảnh tạm trên Windows
    # (một số PNG RGBA có thể làm Tesseract báo std::bad_alloc khi đi qua file tạm).
    command = [
        str(_tesseract_path),
        str(Path(image_path).resolve()),
        "stdout",
        "-l",
        "vie+eng",
    ]
    if (_local_tessdata / "vie.traineddata").exists():
        command.extend(["--tessdata-dir", str(_local_tessdata)])

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            check=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return ""

    return completed.stdout.decode("utf-8", errors="replace").strip()


def extract_text_with_boxes(image_path: str):
    """
    Trích văn bản kèm tọa độ bounding box của từng từ — dùng để highlight
    trực tiếp lên ảnh gốc ở phía frontend.

    Returns:
        List các dict: {"text": str, "left": int, "top": int, "width": int, "height": int, "conf": float}
    """
    image = Image.open(image_path)
    data = pytesseract.image_to_data(image, lang="vie+eng", output_type=pytesseract.Output.DICT)

    boxes = []
    for i, word in enumerate(data["text"]):
        if word.strip() == "":
            continue
        boxes.append({
            "text": word,
            "left": data["left"][i],
            "top": data["top"][i],
            "width": data["width"][i],
            "height": data["height"][i],
            "conf": float(data["conf"][i]),
        })
    return boxes

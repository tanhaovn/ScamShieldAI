"""
Module OCR: trích văn bản tiếng Việt từ ảnh (hóa đơn, screenshot tin nhắn...).

Dùng pytesseract (wrapper của Tesseract OCR) vì dễ cài đặt.
Yêu cầu cài đặt hệ thống (Ubuntu/Debian):
    sudo apt-get install tesseract-ocr tesseract-ocr-vie

Nếu muốn độ chính xác cao hơn cho tiếng Việt, có thể thay bằng PaddleOCR
(pip install paddleocr paddlepaddle) — API tương tự, chỉ cần đổi hàm extract_text().
"""
import csv
import io
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
    if not Path(_tesseract_path).exists():
        return []

    command = [
        str(_tesseract_path),
        str(Path(image_path).resolve()),
        "stdout",
        "-l",
        "vie+eng",
    ]
    if (_local_tessdata / "vie.traineddata").exists():
        command.extend(["--tessdata-dir", str(_local_tessdata)])
    # Do not use the bundled "tsv" config file here: ``--tessdata-dir``
    # points to the project's language-data folder, which intentionally only
    # contains ``vie.traineddata`` and ``eng.traineddata``. Ask Tesseract to
    # generate TSV directly so OCR text and word coordinates are both returned.
    command.extend(["-c", "tessedit_create_tsv=1"])

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            check=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return []

    output = completed.stdout.decode("utf-8", errors="replace")
    boxes = []
    for row in csv.DictReader(io.StringIO(output), delimiter="\t"):
        word = (row.get("text") or "").strip()
        if not word or row.get("level") != "5":
            continue
        try:
            boxes.append(
                {
                    "text": word,
                    "left": int(row["left"]),
                    "top": int(row["top"]),
                    "width": int(row["width"]),
                    "height": int(row["height"]),
                    "conf": float(row.get("conf") or 0),
                    "block_num": int(row.get("block_num") or 0),
                    "par_num": int(row.get("par_num") or 0),
                    "line_num": int(row.get("line_num") or 0),
                    "word_num": int(row.get("word_num") or 0),
                }
            )
        except (KeyError, TypeError, ValueError):
            continue
    return boxes


def extract_text_and_boxes(image_path: str) -> tuple[str, list[dict]]:
    """Run OCR once, returning readable lines and their word coordinates."""
    boxes = extract_text_with_boxes(image_path)
    lines: list[str] = []
    current_line_key = None
    current_line_words: list[str] = []
    for word in boxes:
        line_key = (word["block_num"], word["par_num"], word["line_num"])
        if current_line_key is not None and line_key != current_line_key:
            lines.append(" ".join(current_line_words))
            current_line_words = []
        current_line_key = line_key
        current_line_words.append(word["text"])
    if current_line_words:
        lines.append(" ".join(current_line_words))
    return "\n".join(lines).strip(), boxes


def get_image_dimensions(image_path: str) -> dict[str, int]:
    with Image.open(image_path) as image:
        width, height = image.size
    return {"width": int(width), "height": int(height)}

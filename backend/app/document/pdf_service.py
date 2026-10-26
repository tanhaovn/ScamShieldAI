"""Extract embedded text, OCR scanned pages and QR payloads from PDF files."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from backend.app.ocr.ocr_service import extract_text
from backend.app.visual.qr_analysis import decode_qr_codes


def extract_pdf_content(pdf_path: str, max_pages: int = 10) -> dict:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("Máy chủ chưa cài PyMuPDF để đọc PDF") from exc

    path = Path(pdf_path)
    text_parts: list[str] = []
    qr_values: list[str] = []

    try:
        document = fitz.open(path)
    except Exception as exc:
        raise ValueError("File PDF không hợp lệ hoặc đã bị hỏng") from exc

    page_count = len(document)
    processed_pages = min(page_count, max_pages)
    try:
        with TemporaryDirectory(prefix="scam-pdf-") as temp_dir:
            temp_root = Path(temp_dir)
            for index in range(processed_pages):
                page = document[index]
                embedded_text = (page.get_text("text") or "").strip()

                pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                page_image = temp_root / f"page-{index + 1}.png"
                pixmap.save(page_image)

                page_text = embedded_text
                if len(embedded_text) < 30:
                    page_text = extract_text(str(page_image)).strip()
                if page_text:
                    text_parts.append(f"--- Trang {index + 1} ---\n{page_text}")

                qr_values.extend(decode_qr_codes(str(page_image)))
    finally:
        document.close()

    return {
        "text": "\n\n".join(text_parts).strip(),
        "qr_codes": list(dict.fromkeys(qr_values)),
        "page_count": page_count,
        "processed_pages": processed_pages,
        "truncated": page_count > max_pages,
    }

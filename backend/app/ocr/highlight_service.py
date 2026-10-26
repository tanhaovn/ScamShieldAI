"""Map suspicious OCR terms back to word boxes on the original image."""
from __future__ import annotations

import re
import unicodedata


def _normalize(value: str) -> str:
    value = value.lower().translate(str.maketrans({"đ": "d"}))
    value = "".join(
        character
        for character in unicodedata.normalize("NFD", value)
        if unicodedata.category(character) != "Mn"
    )
    return re.sub(r"\s+", " ", value).strip()


def _compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", _normalize(value))


def _reason_for(label: str, kind: str) -> tuple[str, str]:
    normalized = _normalize(label)
    if kind == "url":
        return "danger", "Đường link này có dấu hiệu giả mạo hoặc dẫn tới trang không an toàn."
    if "otp" in normalized or "mat khau" in normalized:
        return "danger", "Đây là thông tin bí mật; tổ chức hợp pháp không yêu cầu gửi mã này."
    if "chuyen khoan" in normalized or "thanh toan" in normalized:
        return "danger", "Nội dung đang thúc giục thực hiện giao dịch tiền."
    if "khoa" in normalized or "gap" in normalized or "ngay" in normalized:
        return "warning", "Cụm từ tạo cảm giác khẩn cấp để người đọc hành động vội vàng."
    return "warning", "Cụm từ này thường xuất hiện trong các nội dung lừa đảo đã biết."


def build_suspicious_regions(
    words: list[dict],
    highlighted_terms: list[str],
    suspicious_urls: list[str],
) -> list[dict]:
    """Return non-overlapping image regions for matched terms and URLs."""
    if not words:
        return []

    candidates = [
        *((term, "term") for term in highlighted_terms),
        *((url, "url") for url in suspicious_urls),
    ]
    candidates = sorted(
        ((label.strip(), kind) for label, kind in candidates if label and len(label.strip()) > 1),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    regions: list[dict] = []
    claimed_word_indexes: set[int] = set()
    for label, kind in candidates:
        needle = _normalize(label)
        compact_needle = _compact(label)
        expected_words = max(1, len(needle.split()))
        max_window = min(len(words), expected_words + 3, 10)
        matches: list[tuple[int, int, int, int]] = []
        for start in range(len(words)):
            if start in claimed_word_indexes:
                continue
            for length in range(1, max_window + 1):
                end = start + length
                if end > len(words):
                    break
                indexes = range(start, end)
                if any(index in claimed_word_indexes for index in indexes):
                    continue
                window = words[start:end]
                line_keys = {
                    (word.get("block_num"), word.get("par_num"), word.get("line_num"))
                    for word in window
                }
                if len(line_keys) > 1:
                    continue
                joined = _normalize(" ".join(word["text"] for word in window))
                compact_joined = _compact(joined)
                if needle not in joined and compact_needle not in compact_joined:
                    continue
                extra_characters = max(0, len(compact_joined) - len(compact_needle))
                matches.append((extra_characters, length, start, end))

        if not matches:
            continue
        _extra, _length, start, end = min(matches)
        window = words[start:end]
        indexes = range(start, end)
        left = min(word["left"] for word in window)
        top = min(word["top"] for word in window)
        right = max(word["left"] + word["width"] for word in window)
        bottom = max(word["top"] + word["height"] for word in window)
        severity, reason = _reason_for(label, kind)
        regions.append(
            {
                "label": label,
                "kind": kind,
                "severity": severity,
                "reason": reason,
                "left": left,
                "top": top,
                "width": max(1, right - left),
                "height": max(1, bottom - top),
                "confidence": round(
                    sum(max(0.0, word.get("conf", 0.0)) for word in window)
                    / len(window),
                    1,
                ),
            }
        )
        claimed_word_indexes.update(indexes)

    return regions

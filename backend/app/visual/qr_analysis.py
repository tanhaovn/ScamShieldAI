"""Decode QR codes from uploaded images without opening their contents."""
from __future__ import annotations


def decode_qr_codes(image_path: str) -> list[str]:
    """Return unique QR payloads found in an image; fail closed if OpenCV is absent."""
    try:
        import cv2
    except ImportError:
        return []

    image = cv2.imread(str(image_path))
    if image is None:
        return []

    detector = cv2.QRCodeDetector()
    values: list[str] = []

    try:
        detected, decoded_info, _points, _straight = detector.detectAndDecodeMulti(image)
        if detected:
            values.extend(value.strip() for value in decoded_info if value and value.strip())
    except (AttributeError, cv2.error):
        pass

    if not values:
        try:
            value, _points, _straight = detector.detectAndDecode(image)
            if value and value.strip():
                values.append(value.strip())
        except cv2.error:
            pass

    return list(dict.fromkeys(values))

import cv2
import fitz
from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)
SUSPICIOUS_URL = "https://tiktokshopseller-vn.com/login"


def test_direct_text_and_url_inputs_use_shared_risk_pipeline():
    text_response = client.post(
        "/check-text",
        json={"text": f"Tài khoản sẽ bị khóa. Xác minh OTP ngay tại {SUSPICIOUS_URL}"},
    )
    url_response = client.post("/check-url", json={"url": SUSPICIOUS_URL})

    assert text_response.status_code == 200
    assert text_response.json()["source_type"] == "text"
    assert text_response.json()["risk_level"] == "nguy_hiem"
    assert url_response.status_code == 200
    assert url_response.json()["source_type"] == "url"
    assert url_response.json()["phishvn_urls"]


def test_invalid_direct_url_is_rejected():
    response = client.post("/check-url", json={"url": "đây không phải URL"})
    assert response.status_code == 422


def test_pdf_embedded_text_is_extracted_and_analyzed(tmp_path):
    pdf_path = tmp_path / "payment-notice.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        f"THONG BAO THANH TOAN - XAC MINH OTP NGAY TAI {SUSPICIOUS_URL}",
    )
    document.save(pdf_path)
    document.close()

    with pdf_path.open("rb") as source:
        response = client.post(
            "/check-document",
            files={"file": (pdf_path.name, source, "application/pdf")},
        )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["source_type"] == "pdf"
    assert payload["document_info"]["processed_pages"] == 1
    assert "tiktokshopseller" in payload["extracted_text"].lower()


def test_qr_in_image_is_decoded_before_url_analysis(tmp_path):
    image_path = tmp_path / "qr.png"
    qr_image = cv2.QRCodeEncoder_create().encode(SUSPICIOUS_URL)
    qr_image = cv2.resize(
        qr_image,
        None,
        fx=14,
        fy=14,
        interpolation=cv2.INTER_NEAREST,
    )
    cv2.imwrite(str(image_path), qr_image)

    with image_path.open("rb") as source:
        response = client.post(
            "/check-image",
            files={"file": (image_path.name, source, "image/png")},
        )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["qr_codes"] == [SUSPICIOUS_URL]
    assert payload["phishvn_urls"]
    assert payload["image_dimensions"]["width"] > 0
    assert isinstance(payload["image_annotations"], list)

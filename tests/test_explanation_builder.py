from types import SimpleNamespace

from backend.app.ai.phishvn_url_model import PhishVNTextResult, UrlPrediction
from backend.app.risk.explanation_builder import build_analysis_explanation
from backend.app.risk.risk_engine import RiskResult


def test_structured_explanation_names_the_strongest_signal():
    text_result = RiskResult(
        risk_score=15,
        risk_level="an_toan",
        scam_type="phishing",
        highlighted_terms=["xác minh ngay"],
    )
    phishvn_result = PhishVNTextResult(
        available=True,
        model_name="PhishVN-HistGB",
        risk_score=87,
        predictions=[
            UrlPrediction(
                url="tiktokshopseller-vn.com",
                normalized_url="tiktokshopseller-vn.com",
                domain="tiktokshopseller-vn.com",
                probability=0.8743,
                label="phishing",
                risk_score=87,
                suspicious_signals=[
                    "có chuỗi 'tiktok' gợi tên thương hiệu nhưng domain không thuộc tiktok.com"
                ],
            )
        ],
    )
    visual_result = SimpleNamespace(visual_score=8, flags=["Ảnh không có metadata EXIF"])
    image_model_result = SimpleNamespace(available=False, explanation="")

    explanation, breakdown = build_analysis_explanation(
        extracted_text="Xác minh ngay tại tiktokshopseller-vn.com",
        text_result=text_result,
        phishvn_result=phishvn_result,
        visual_result=visual_result,
        image_model_result=image_model_result,
        image_model_score=0,
        combined_score=87,
        combined_level="nguy_hiem",
    )

    assert "KẾT LUẬN: Nguy hiểm (87/100)" in explanation
    assert "Nguồn đóng góp lớn nhất là URL PhishVN" in explanation
    assert breakdown["verdict"]["score"] == 87
    assert [item["key"] for item in breakdown["components"]] == ["text", "url", "visual"]
    assert "tiktok.com" in breakdown["components"][1]["findings"][1]

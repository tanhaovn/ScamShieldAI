from types import SimpleNamespace

from PIL import Image

import backend.app.services.analysis as analysis_service


def test_confident_vlm_safe_overrides_isolated_resnet_false_positive(tmp_path, monkeypatch):
    image_path = tmp_path / "ordinary-person.jpg"
    Image.new("RGB", (640, 480), color=(185, 175, 165)).save(image_path)

    monkeypatch.setattr(
        analysis_service,
        "analyze_phishing_image",
        lambda _path: SimpleNamespace(
            available=True,
            probability=0.80,
            label="phishing",
            explanation="Noisy ResNet prediction",
            gradcam_available=False,
            gradcam_path="",
            gradcam_target_class="phishing",
            gradcam_note="",
            gradcam_focus_regions=[],
        ),
    )
    monkeypatch.setattr(
        analysis_service,
        "analyze_image_visual",
        lambda _path, use_deepfake_model=False: SimpleNamespace(visual_score=0, flags=[]),
    )
    monkeypatch.setattr(
        analysis_service,
        "analyze_image_context",
        lambda *_args, **_kwargs: SimpleNamespace(
            available=True,
            verdict="safe",
            confidence=0.95,
            risk_score=10,
            risk_indicators=["Ảnh người ngồi trong phòng"],
            observed_text=[],
            reasoning="Không có dấu hiệu lừa đảo trong ảnh đời thường.",
            recommended_action="Không cần hành động.",
            model_name="gemini-test",
            note="",
            chain_of_thought=[],
            explanation_source="vision_language_model",
            explanation_items=[
                {
                    "observation": "Ảnh người ngồi trong phòng",
                    "location": "toàn ảnh",
                    "why_risky": "Không có yêu cầu chuyển tiền hay cung cấp thông tin.",
                }
            ],
        ),
    )

    payload = analysis_service.analyze_content_payload(
        "", image_path=str(image_path), qr_codes=[]
    )

    assert payload["image_model_score"] == 80
    assert payload["vlm_analysis"]["verdict"] == "safe"
    assert payload["risk_level"] == "an_toan"
    assert payload["risk_score"] <= 15
    assert payload["scam_type"] != "phishing"

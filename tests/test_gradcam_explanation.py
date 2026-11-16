from pathlib import Path
import shutil

import pytest

from backend.app.ai.phishing_model import MODEL_PATH, analyze_phishing_image


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="ResNet18 checkpoint is not available")
def test_resnet_generates_gradcam_explanation(tmp_path):
    pytest.importorskip("pytorch_grad_cam")
    source = Path("tests/fixtures/images/lua_dao_scam/02_amazon_fake_login.png")
    if not source.exists():
        pytest.skip("Grad-CAM fixture is not available")

    image_path = tmp_path / "phishing-screenshot.png"
    shutil.copyfile(source, image_path)

    result = analyze_phishing_image(str(image_path))

    assert result.available is True
    assert 0.0 <= result.probability <= 1.0
    assert result.gradcam_available is True, result.gradcam_note
    assert result.gradcam_target_class == result.label
    assert Path(result.gradcam_path).is_file()
    assert Path(result.gradcam_path).name == "phishing-screenshot.gradcam.jpg"
    assert "không tự chứng minh" in result.gradcam_note
    assert isinstance(result.gradcam_focus_regions, list)


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="ResNet18 checkpoint is not available")
def test_gradcam_explains_legitimate_prediction_too(tmp_path):
    pytest.importorskip("pytorch_grad_cam")
    source = Path("tests/fixtures/images/an_toan_safe/02_web_cong_ty_chuan.png")
    if not source.exists():
        pytest.skip("Grad-CAM fixture is not available")

    image_path = tmp_path / "legitimate-screenshot.png"
    shutil.copyfile(source, image_path)

    result = analyze_phishing_image(str(image_path))

    assert result.available is True
    assert result.label == "legitimate"
    assert result.gradcam_available is True, result.gradcam_note
    assert result.gradcam_target_class == "legitimate"
    assert Path(result.gradcam_path).is_file()

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from backend.app.ai.domain_intelligence import inspect_urls
from backend.app.ai.google_safe_browsing import check_urls as check_google_safe_browsing
from backend.app.ai.phishing_model import analyze_phishing_image
from backend.app.ai.phishvn_url_model import analyze_urls_in_text, extract_url_candidates
from backend.app.ai.vlm_image_analyzer import analyze_image_context
from backend.app.core.config import APP_VERSION, UPLOAD_DIR, USE_DEEPFAKE_MODEL
from backend.app.risk.explanation_builder import build_analysis_explanation
from backend.app.risk.risk_engine import analyze_text
from backend.app.services.runtime import GIT_COMMIT
from backend.app.visual.visual_forensics import analyze_image_visual


def analyze_content_payload(
    content: str,
    *,
    image_path: str | None = None,
    qr_codes: list[str] | None = None,
) -> dict:
    """Run the shared text, URL and optional visual pipeline."""
    qr_codes = qr_codes or []
    analysis_text = "\n".join(part for part in [content.strip(), *qr_codes] if part).strip()
    url_candidates = extract_url_candidates(analysis_text)
    domain_intelligence = inspect_urls(url_candidates)

    # Only the remote reputation lookup is overlapped with local inference.
    # Running several native ML runtimes (Torch/OpenMP/OpenCV) concurrently can
    # oversubscribe CPUs or stall on Windows, so the accuracy-critical local
    # models intentionally remain sequential and deterministic.
    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="reputation") as executor:
        safe_browsing_future = executor.submit(
            check_google_safe_browsing,
            url_candidates,
        )
        text_result = analyze_text(analysis_text)
        phishvn_result = analyze_urls_in_text(analysis_text)
        if image_path:
            visual_result = analyze_image_visual(
                image_path, use_deepfake_model=USE_DEEPFAKE_MODEL
            )
            image_model_result = analyze_phishing_image(image_path)
        safe_browsing_result = safe_browsing_future.result()

    domain_score = max(
        (int(item.get("score") or 0) for item in domain_intelligence),
        default=0,
    )
    trusted_domains_only = bool(domain_intelligence) and all(
        bool(item.get("trusted")) for item in domain_intelligence
    )
    raw_phishvn_score = int(phishvn_result.risk_score)
    calibrated_phishvn_score = raw_phishvn_score
    if (
        trusted_domains_only
        and int(text_result.risk_score) < 25
        and not safe_browsing_result.matches
    ):
        calibrated_phishvn_score = 0
    elif (
        raw_phishvn_score >= 60
        and domain_score < 50
        and int(text_result.risk_score) < 25
        and not safe_browsing_result.matches
    ):
        calibrated_phishvn_score = 45

    if image_path:
        image_model_score = int(image_model_result.probability * 100)
        vlm_result = analyze_image_context(
            image_path,
            ocr_text=analysis_text,
            qr_codes=qr_codes,
            visual_flags=visual_result.flags,
            image_model_probability=(
                image_model_result.probability if image_model_result.available else None
            ),
            phishvn_url_score=int(phishvn_result.risk_score),
            phishvn_predictions=(
                phishvn_result.predictions_as_dicts()
                if hasattr(phishvn_result, "predictions_as_dicts")
                else []
            ),
            gradcam_path=str(getattr(image_model_result, "gradcam_path", "") or ""),
            gradcam_focus_regions=list(
                getattr(image_model_result, "gradcam_focus_regions", None) or []
            ),
            image_model_label=str(
                getattr(image_model_result, "label", "unavailable") or "unavailable"
            ),
        )
    else:
        visual_result = SimpleNamespace(visual_score=0, flags=[])
        image_model_result = SimpleNamespace(
            available=False,
            probability=0.0,
            label="not_applicable",
            explanation="Không áp dụng model hình ảnh cho nguồn dữ liệu này.",
        )
        image_model_score = 0
        vlm_result = SimpleNamespace(
            available=False,
            risk_score=0,
            verdict="not_applicable",
            confidence=0.0,
            risk_indicators=[],
            observed_text=[],
            reasoning="",
            recommended_action="",
            model_name="Vision-Language Model",
            note="Không áp dụng phân tích ngữ cảnh ảnh cho nguồn dữ liệu này.",
        )

    vlm_confident_safe = bool(
        image_path
        and getattr(vlm_result, "available", False)
        and getattr(vlm_result, "verdict", "") == "safe"
        and float(getattr(vlm_result, "confidence", 0.0) or 0.0) >= 0.65
        and getattr(vlm_result, "explanation_source", "") == "vision_language_model"
        and int(text_result.risk_score) < 25
        and calibrated_phishvn_score < 25
        and domain_score < 20
        and not safe_browsing_result.matches
    )

    primary_scores = [int(text_result.risk_score)]
    if (
        phishvn_result.available
        and phishvn_result.predictions
        and calibrated_phishvn_score
    ):
        primary_scores.append(calibrated_phishvn_score)
    if domain_score >= 20:
        primary_scores.append(domain_score)
    if safe_browsing_result.matches:
        primary_scores.append(int(safe_browsing_result.risk_score))
    if image_path and vlm_result.available:
        primary_scores.append(int(vlm_result.risk_score))
    if (
        image_path
        and image_model_result.available
        and image_model_score >= 70
        and not vlm_confident_safe
    ):
        primary_scores.append(image_model_score)

    secondary_scores = []
    if image_path:
        secondary_scores.append(int(visual_result.visual_score))
        if image_model_result.available:
            secondary_scores.append(image_model_score)

    max_primary = max(primary_scores)
    avg_primary = sum(primary_scores) / max(len(primary_scores), 1)

    if image_path and vlm_result.available and vlm_confident_safe:
        combined_score = min(int(max_primary * 0.35), 15)
    elif max_primary >= 60:
        corroborating = [score for score in primary_scores if score >= 40]
        if len(corroborating) >= 2:
            combined_score = int(
                0.75 * max_primary
                + 0.25 * (sum(corroborating) / len(corroborating))
            )
        else:
            combined_score = int(0.85 * max_primary + 0.15 * avg_primary)
    elif max_primary >= 25:
        combined_score = int(0.70 * max_primary + 0.30 * avg_primary)
    else:
        combined_score = int(avg_primary)

    if secondary_scores and max(secondary_scores) >= 50 and combined_score >= 25:
        combined_score = min(100, combined_score + int(0.12 * max(secondary_scores)))

    if domain_score >= 20 and not trusted_domains_only:
        combined_score = max(combined_score, min(domain_score, 70))
    if (
        image_path
        and int(text_result.risk_score) >= 40
        and int(vlm_result.risk_score) >= 45
        and "biểu mẫu đăng nhập/xác thực" in text_result.highlighted_terms
    ):
        combined_score = max(combined_score, 60)
    if (
        trusted_domains_only
        and int(text_result.risk_score) < 25
        and not safe_browsing_result.matches
    ):
        combined_score = min(combined_score, 15)

    combined_score = max(0, min(combined_score, 100))
    if combined_score >= 60:
        combined_level = "nguy_hiem"
    elif combined_score >= 25:
        combined_level = "nghi_ngo"
    else:
        combined_level = "an_toan"

    combined_scam_type = text_result.scam_type
    if safe_browsing_result.matches:
        combined_scam_type = "verified_unsafe_url"
    elif domain_score >= 50:
        combined_scam_type = "phishing_url"
    elif (
        calibrated_phishvn_score >= 50
        and calibrated_phishvn_score >= text_result.risk_score
    ):
        combined_scam_type = "phishing_url"
    elif (
        image_path
        and image_model_result.available
        and image_model_score >= 65
        and combined_scam_type == "none"
        and not vlm_confident_safe
    ):
        combined_scam_type = "phishing"

    suggested_action = text_result.suggested_action
    if safe_browsing_result.matches:
        suggested_action = (
            "Google Safe Browsing đã trả về kết quả khớp với danh sách URL nguy hiểm đã biết. "
            "Không mở URL, không đăng nhập và không cung cấp OTP hoặc thông tin thanh toán."
        )
    elif domain_score >= 50:
        suggested_action = (
            "Cấu trúc tên miền có dấu hiệu giả mạo mạnh. Không mở URL hoặc nhập thông tin; "
            "hãy tự gõ địa chỉ website chính thức để xác minh."
        )
    elif calibrated_phishvn_score >= 60:
        suggested_action = (
            "KHÔNG mở URL, KHÔNG đăng nhập hoặc cung cấp OTP/thông tin thanh toán. "
            "Hãy tự nhập địa chỉ website chính thức hoặc liên hệ tổ chức qua kênh đã xác minh."
        )
    elif phishvn_result.risk_score >= 25 and text_result.risk_score < 25:
        suggested_action = (
            "URL có dấu hiệu cần kiểm tra thêm. Không bấm trực tiếp; hãy đối chiếu tên miền "
            "với website chính thức trước khi tiếp tục."
        )
    elif (
        image_path
        and image_model_result.available
        and image_model_score >= 65
        and not vlm_confident_safe
    ):
        suggested_action = (
            "Ảnh có bố cục tương đồng với các trang giả mạo. Không nhập mật khẩu, OTP hoặc "
            "thông tin thanh toán; hãy tự mở ứng dụng hay website chính thức để xác minh."
        )

    combined_explanation, analysis_breakdown = build_analysis_explanation(
        extracted_text=analysis_text,
        text_result=text_result,
        phishvn_result=phishvn_result,
        safe_browsing_result=safe_browsing_result,
        phishvn_display_score=calibrated_phishvn_score,
        domain_intelligence=domain_intelligence,
        visual_result=visual_result,
        image_model_result=image_model_result,
        image_model_score=image_model_score,
        vlm_result=vlm_result,
        combined_score=combined_score,
        combined_level=combined_level,
        include_visual=bool(image_path),
    )

    gradcam_path_value = str(getattr(image_model_result, "gradcam_path", "") or "")
    gradcam_url = ""
    if gradcam_path_value:
        gradcam_path = Path(gradcam_path_value)
        try:
            relative_gradcam_path = gradcam_path.resolve().relative_to(UPLOAD_DIR.resolve())
            if gradcam_path.is_file():
                gradcam_url = f"/uploads/{relative_gradcam_path.as_posix()}"
        except ValueError:
            gradcam_url = ""
    gradcam_target_class = str(
        getattr(image_model_result, "gradcam_target_class", "") or ""
    )
    gradcam_target_score = (
        image_model_score
        if gradcam_target_class == "phishing"
        else 100 - image_model_score
    )

    return {
        "extracted_text": content,
        "risk_score": combined_score,
        "risk_level": combined_level,
        "text_risk_score": text_result.risk_score,
        "phishvn_available": phishvn_result.available,
        "phishvn_model": phishvn_result.model_name,
        "phishvn_url_risk_score": calibrated_phishvn_score,
        "phishvn_raw_score": raw_phishvn_score,
        "phishvn_calibrated_score": calibrated_phishvn_score,
        "phishvn_urls": phishvn_result.predictions_as_dicts(),
        "google_safe_browsing": safe_browsing_result.to_dict(),
        "domain_intelligence": domain_intelligence,
        "visual_risk_score": visual_result.visual_score,
        "image_model_available": image_model_result.available,
        "image_model_label": image_model_result.label,
        "image_model_score": image_model_score,
        "image_model_gradcam": {
            "available": bool(
                getattr(image_model_result, "gradcam_available", False) and gradcam_url
            ),
            "image_url": gradcam_url,
            "method": "Grad-CAM",
            "target_class": gradcam_target_class,
            "target_score": gradcam_target_score if gradcam_target_class else 0,
            "target_layer": "layer4[-1]",
            "note": str(getattr(image_model_result, "gradcam_note", "") or ""),
            "focus_regions": list(
                getattr(image_model_result, "gradcam_focus_regions", None) or []
            ),
        },
        "vlm_analysis": (
            vlm_result.to_dict() if hasattr(vlm_result, "to_dict") else vars(vlm_result)
        ),
        "scam_type": combined_scam_type,
        "highlighted_terms": text_result.highlighted_terms,
        "visual_flags": visual_result.flags,
        "qr_codes": qr_codes,
        "explanation": combined_explanation,
        "analysis_breakdown": analysis_breakdown,
        "suggested_action": suggested_action,
        "detector": {"app_version": APP_VERSION, "git_commit": GIT_COMMIT},
    }


def local_analysis_response(payload: dict, source_type: str, filename: str) -> dict:
    return {
        **payload,
        "scan_id": None,
        "image_url": "",
        "original_filename": filename,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "storage": "local_storage",
        "source_type": source_type,
        "scam_category_id": None,
    }

from datetime import datetime

from sqlalchemy.orm import Session

from backend.app.db.models import ScanHistory, User


def save_scan_history(
    db: Session,
    user: User,
    analysis: dict,
    *,
    source_type: str,
    original_filename: str,
    image_url: str = "",
    scam_category_id: int | None = None,
    extra_details: dict | None = None,
) -> ScanHistory:
    """Persist one detector result under the authenticated user's account."""
    details = {
        "source_type": source_type,
        "terms": analysis.get("highlighted_terms", []),
        "visual_flags": analysis.get("visual_flags", []),
        "phishvn_urls": analysis.get("phishvn_urls", []),
        "qr_codes": analysis.get("qr_codes", []),
        "analysis_breakdown": analysis.get("analysis_breakdown"),
        "vlm_analysis": analysis.get("vlm_analysis"),
        "image_model_gradcam": analysis.get("image_model_gradcam"),
        **(extra_details or {}),
    }
    row = ScanHistory(
        user_id=user.id,
        image_url=image_url,
        original_filename=original_filename,
        extracted_text=analysis.get("extracted_text", ""),
        scam_category_id=scam_category_id,
        risk_score=int(analysis.get("risk_score") or 0),
        risk_level=analysis.get("risk_level") or "an_toan",
        explanation=analysis.get("explanation"),
        highlighted_regions=details,
        suggested_action=analysis.get("suggested_action"),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def account_analysis_response(
    analysis: dict,
    row: ScanHistory,
    *,
    source_type: str,
    original_filename: str,
) -> dict:
    created_at = row.created_at or datetime.utcnow()
    return {
        **analysis,
        "scan_id": row.id,
        "image_url": row.image_url or "",
        "original_filename": original_filename,
        "created_at": created_at.isoformat(),
        "storage": "database",
        "source_type": source_type,
        "scam_category_id": row.scam_category_id,
    }

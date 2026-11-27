from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user
from backend.app.db.database import get_db
from backend.app.db.models import ScanHistory, User


router = APIRouter(tags=["History"])


@router.get("/scan-history")
def list_scan_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(ScanHistory)
        .filter(ScanHistory.user_id == current_user.id)
        .order_by(ScanHistory.created_at.desc())
        .all()
    )
    results = []
    for row in rows:
        details = row.highlighted_regions if isinstance(row.highlighted_regions, dict) else {}
        results.append(
            {
                "id": row.id,
                "image_url": row.image_url,
                "original_filename": row.original_filename,
                "risk_score": row.risk_score,
                "risk_level": row.risk_level,
                "scam_category_id": row.scam_category_id,
                "extracted_text": row.extracted_text,
                "explanation": row.explanation,
                "suggested_action": row.suggested_action,
                "highlighted_regions": row.highlighted_regions,
                "highlighted_terms": details.get("terms", []),
                "visual_flags": details.get("visual_flags", []),
                "phishvn_urls": details.get("phishvn_urls", []),
                "qr_codes": details.get("qr_codes", []),
                "image_annotations": details.get("image_annotations", []),
                "image_dimensions": details.get("image_dimensions"),
                "analysis_breakdown": details.get("analysis_breakdown"),
                "vlm_analysis": details.get("vlm_analysis"),
                "image_model_gradcam": details.get("image_model_gradcam"),
                "source_type": details.get("source_type", "image"),
                "created_at": row.created_at,
            }
        )
    return results


@router.get("/history/{user_id}")
def get_history(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới xem lịch sử máy chủ")
    records = (
        db.query(ScanHistory)
        .filter(ScanHistory.user_id == user_id)
        .order_by(ScanHistory.created_at.desc())
        .all()
    )
    return [
        {
            "scan_id": row.id,
            "image_url": row.image_url,
            "risk_score": row.risk_score,
            "risk_level": row.risk_level,
            "scam_category_id": row.scam_category_id,
            "created_at": row.created_at,
        }
        for row in records
    ]

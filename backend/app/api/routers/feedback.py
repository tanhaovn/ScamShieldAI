from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user
from backend.app.db.database import get_db
from backend.app.db.models import ScanFeedback, User
from backend.app.schemas.scan import ScanFeedbackRequest


router = APIRouter(tags=["Feedback"])


@router.post("/scan-feedback", status_code=201)
def create_scan_feedback(
    payload: ScanFeedbackRequest,
    db: Session = Depends(get_db),
):
    feedback = ScanFeedback(
        scan_id=payload.scan_id,
        client_scan_id=payload.client_scan_id,
        verdict=payload.verdict,
        predicted_level=payload.predicted_level,
        risk_score=payload.risk_score,
        source_type=payload.source_type,
        original_filename=payload.original_filename,
        note=(payload.note or "").strip() or None,
        evidence_snapshot={
            "highlighted_terms": payload.highlighted_terms[:30],
            "urls": payload.urls[:20],
        },
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return {"id": feedback.id, "status": feedback.review_status}


@router.get("/scan-feedback")
def list_scan_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới xem phản hồi")
    rows = (
        db.query(ScanFeedback)
        .order_by(ScanFeedback.created_at.desc())
        .limit(500)
        .all()
    )
    return [
        {
            "id": row.id,
            "scan_id": row.scan_id,
            "client_scan_id": row.client_scan_id,
            "verdict": row.verdict,
            "predicted_level": row.predicted_level,
            "risk_score": row.risk_score,
            "source_type": row.source_type,
            "original_filename": row.original_filename,
            "note": row.note,
            "review_status": row.review_status,
            "created_at": row.created_at,
        }
        for row in rows
    ]

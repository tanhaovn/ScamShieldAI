from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user
from backend.app.core.config import APP_VERSION
from backend.app.db.database import get_db
from backend.app.db.models import (
    AiModel,
    ModelEvaluation,
    ScamCategory,
    ScamKeyword,
    SystemActivityLog,
    TrainingDataset,
    User,
)
from backend.app.evaluation.benchmark import run_detector_benchmark
from backend.app.schemas.admin import (
    AiModelRequest,
    ModelEvaluationRequest,
    ScamKeywordRequest,
    SystemLogRequest,
    TrainingDatasetRequest,
)
from backend.app.services.analysis import analyze_content_payload
from backend.app.services.runtime import GIT_COMMIT, runtime_info


router = APIRouter(tags=["Administration"])


@router.get("/scam-categories")
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(ScamCategory).order_by(ScamCategory.id.asc()).all()
    return [
        {
            "id": item.id,
            "code": item.code,
            "display_name": item.display_name,
            "description": item.description,
        }
        for item in categories
    ]


@router.get("/training-dataset")
def list_training_dataset(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(TrainingDataset)
    if current_user.role != "admin":
        query = query.filter(TrainingDataset.uploaded_by == current_user.id)
    rows = query.order_by(TrainingDataset.created_at.desc()).all()
    return [
        {
            "id": row.id,
            "image_url": row.image_url,
            "scam_category_id": row.scam_category_id,
            "is_anonymized": row.is_anonymized,
            "is_verified": row.is_verified,
            "uploaded_by": row.uploaded_by,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.post("/training-dataset")
def create_training_dataset(
    payload: TrainingDatasetRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới được upload dataset huấn luyện")
    dataset = TrainingDataset(
        image_url=payload.image_url,
        scam_category_id=payload.scam_category_id,
        is_anonymized=payload.is_anonymized,
        is_verified=payload.is_verified,
        uploaded_by=current_user.id,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return {"id": dataset.id, "image_url": dataset.image_url}


@router.get("/ai-models")
def list_ai_models(db: Session = Depends(get_db)):
    return [
        {
            "id": item.id,
            "version_name": item.version_name,
            "description": item.description,
            "is_active": item.is_active,
            "created_at": item.created_at,
        }
        for item in db.query(AiModel).order_by(AiModel.created_at.desc()).all()
    ]


@router.post("/ai-models")
def create_ai_model(
    payload: AiModelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới được quản lý model")
    model = AiModel(
        version_name=payload.version_name,
        description=payload.description,
        is_active=payload.is_active,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return {"id": model.id, "version_name": model.version_name}


@router.get("/model-evaluations")
def list_model_evaluations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới xem đánh giá model")
    rows = db.query(ModelEvaluation).order_by(ModelEvaluation.evaluated_at.desc()).all()
    return [
        {
            "id": row.id,
            "ai_model_id": row.ai_model_id,
            "macro_f1": row.macro_f1,
            "recall": row.recall,
            "false_alarm_rate": row.false_alarm_rate,
            "explanation_usefulness": row.explanation_usefulness,
            "evaluated_at": row.evaluated_at,
        }
        for row in rows
    ]


@router.post("/model-evaluations")
def create_model_evaluation(
    payload: ModelEvaluationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới được ghi đánh giá model")
    evaluation = ModelEvaluation(
        ai_model_id=payload.ai_model_id,
        macro_f1=payload.macro_f1,
        recall=payload.recall,
        false_alarm_rate=payload.false_alarm_rate,
        explanation_usefulness=payload.explanation_usefulness,
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return {"id": evaluation.id}


@router.post("/model-evaluations/run")
def run_model_evaluation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới được chạy đánh giá model")

    result = run_detector_benchmark(analyze_content_payload)
    active_model = (
        db.query(AiModel)
        .filter(AiModel.is_active.is_(True))
        .order_by(AiModel.created_at.desc())
        .first()
    )
    saved_evaluation_id = None
    if active_model:
        evaluation = ModelEvaluation(
            ai_model_id=active_model.id,
            macro_f1=result["macro_f1"],
            recall=result["binary"]["recall"],
            false_alarm_rate=result["binary"]["false_alarm_rate"],
            explanation_usefulness=None,
        )
        db.add(evaluation)
        db.flush()
        saved_evaluation_id = evaluation.id
        db.add(
            SystemActivityLog(
                admin_id=current_user.id,
                action_type="automated_model_evaluation",
                description=(
                    f"{result['suite']}: {result['passed']}/{result['total']} passed; "
                    f"version={APP_VERSION}; commit={GIT_COMMIT}"
                ),
            )
        )
        db.commit()
    return {
        **result,
        "runtime": runtime_info(),
        "active_model_id": active_model.id if active_model else None,
        "saved_evaluation_id": saved_evaluation_id,
    }


@router.get("/system-logs")
def list_system_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới xem log hệ thống")
    rows = db.query(SystemActivityLog).order_by(SystemActivityLog.created_at.desc()).all()
    return [
        {
            "id": row.id,
            "admin_id": row.admin_id,
            "action_type": row.action_type,
            "description": row.description,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.post("/system-logs")
def create_system_log(
    payload: SystemLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới được ghi log hệ thống")
    log = SystemActivityLog(
        admin_id=current_user.id,
        action_type=payload.action_type,
        description=payload.description,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"id": log.id, "action_type": log.action_type}


@router.get("/scam-keywords")
def list_scam_keywords(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới xem từ khóa")
    rows = db.query(ScamKeyword).order_by(
        ScamKeyword.category,
        ScamKeyword.weight.desc(),
    ).all()
    return [
        {
            "id": row.id,
            "keyword": row.keyword,
            "category": row.category,
            "weight": row.weight,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.post("/scam-keywords", status_code=201)
def create_scam_keyword(
    payload: ScamKeywordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới quản lý từ khóa")
    keyword = payload.keyword.strip().lower()
    if db.query(ScamKeyword).filter(ScamKeyword.keyword == keyword).first():
        raise HTTPException(status_code=409, detail="Từ khóa đã tồn tại")
    row = ScamKeyword(
        keyword=keyword,
        category=payload.category.strip(),
        weight=payload.weight,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "keyword": row.keyword,
        "category": row.category,
        "weight": row.weight,
    }

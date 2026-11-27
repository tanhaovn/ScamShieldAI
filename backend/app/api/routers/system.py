from fastapi import APIRouter

from backend.app.services.runtime import runtime_info


router = APIRouter(tags=["System"])


@router.get("/health")
def health_check():
    return runtime_info()


@router.get("/version")
def version_info():
    return runtime_info()

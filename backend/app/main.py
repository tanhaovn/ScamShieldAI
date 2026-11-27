"""FastAPI application entry point.

Run locally with::

    uvicorn backend.app.main:app --reload

Feature routes live in ``backend.app.api.routers``. Business logic belongs in
``backend.app.services`` so this module stays focused on application assembly.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.dependencies import get_current_user
from backend.app.api.router import api_router
from backend.app.api.routers.system import health_check, version_info
from backend.app.core.config import CORS_ORIGINS, FRONTEND_DIR, UPLOAD_DIR
from backend.app.core.security import decode_token as _decode_token
from backend.app.schemas import (
    AiModelRequest,
    BatchUrlRequest,
    DeviceHeartbeatRequest,
    GoogleAuthRequest,
    LoginRequest,
    ModelEvaluationRequest,
    ProfileUpdateRequest,
    RegisterRequest,
    ScamKeywordRequest,
    ScanFeedbackRequest,
    ScanImageRequest,
    SystemLogRequest,
    TextCheckRequest,
    TrainingDatasetRequest,
    UrlCheckRequest,
)
from backend.app.services.analysis import (
    analyze_content_payload as _analyze_content_payload,
    local_analysis_response as _local_analysis_response,
)
from backend.app.services.startup import initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Vietnamese Scam Detection - Multi-source Scanner",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dist_dir = FRONTEND_DIR / "dist"
if (dist_dir / "assets").exists():
    app.mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets")
app.mount(
    "/static",
    StaticFiles(directory=dist_dir if dist_dir.exists() else FRONTEND_DIR),
    name="static",
)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/", include_in_schema=False)
def dashboard():
    dist_index = dist_dir / "index.html"
    if dist_index.exists():
        return FileResponse(dist_index)
    return FileResponse(FRONTEND_DIR / "index.html")


app.include_router(api_router)


__all__ = [
    "app",
    "health_check",
    "version_info",
    "get_current_user",
    "_analyze_content_payload",
    "_local_analysis_response",
    "_decode_token",
    "AiModelRequest",
    "BatchUrlRequest",
    "DeviceHeartbeatRequest",
    "GoogleAuthRequest",
    "LoginRequest",
    "ModelEvaluationRequest",
    "ProfileUpdateRequest",
    "RegisterRequest",
    "ScamKeywordRequest",
    "ScanFeedbackRequest",
    "ScanImageRequest",
    "SystemLogRequest",
    "TextCheckRequest",
    "TrainingDatasetRequest",
    "UrlCheckRequest",
]

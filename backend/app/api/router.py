from fastapi import APIRouter

from backend.app.api.routers import admin, auth, devices, feedback, history, scans, system

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(scans.router)
api_router.include_router(history.router)
api_router.include_router(feedback.router)
api_router.include_router(devices.router)
api_router.include_router(admin.router)
api_router.include_router(system.router)

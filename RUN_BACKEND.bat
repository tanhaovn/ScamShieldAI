@echo off
title Scam Detector - Backend
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [LOI] Chua co moi truong Python .venv.
    echo Hay chay SETUP_PROJECT.bat truoc.
    pause
    exit /b 1
)

echo Dang khoi dong Backend tai http://127.0.0.1:8000
echo Swagger API: http://127.0.0.1:8000/docs
echo.
if not defined USE_VLM_ANALYZER set USE_VLM_ANALYZER=true
if not defined VLM_MODEL_ID set VLM_MODEL_ID=HuggingFaceTB/SmolVLM-500M-Instruct
if not defined VLM_DEVICE set VLM_DEVICE=auto
if not defined VLM_LOCAL_FILES_ONLY set VLM_LOCAL_FILES_ONLY=true
if not defined VLM_MAX_NEW_TOKENS set VLM_MAX_NEW_TOKENS=140
if not defined HF_HUB_OFFLINE set HF_HUB_OFFLINE=1
if not defined TRANSFORMERS_OFFLINE set TRANSFORMERS_OFFLINE=1
".venv\Scripts\python.exe" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

echo.
echo Backend da dung hoac gap loi.
pause

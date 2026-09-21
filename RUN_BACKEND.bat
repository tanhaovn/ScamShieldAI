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
".venv\Scripts\python.exe" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

echo.
echo Backend da dung hoac gap loi.
pause

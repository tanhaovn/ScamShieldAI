@echo off
setlocal
title Scam Detector - Start Project
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [LOI] Du an chua duoc cai dat.
    echo Hay nhap dup SETUP_PROJECT.bat truoc.
    pause
    exit /b 1
)

if not exist "frontend-react\node_modules" (
    echo [LOI] Chua co thu vien frontend.
    echo Hay nhap dup SETUP_PROJECT.bat truoc.
    pause
    exit /b 1
)

echo Dang mo Backend va Frontend...
start "Scam Detector Backend" "%~dp0RUN_BACKEND.bat"
start "Scam Detector Frontend" "%~dp0RUN_FRONTEND.bat"

echo Cho server khoi dong, sau do mo trinh duyet...
timeout /t 5 /nobreak >nul
start "" "http://127.0.0.1:5173/"

echo.
echo Da khoi dong du an.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:5173
echo API docs: http://127.0.0.1:8000/docs
echo.
echo Muon tat du an: dong hai cua so Backend va Frontend.
timeout /t 3 /nobreak >nul
endlocal

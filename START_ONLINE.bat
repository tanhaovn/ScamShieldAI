@echo off
setlocal
title Scam Detector - Online Public Mode
cd /d "%~dp0"

echo =======================================================
echo   KHOI DONG SCAM DETECTOR CHE DO ONLINE (CONG KHAI)
echo =======================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [LOI] Du an chua duoc cai dat moi truong Python.
    echo Hay nhap dup SETUP_PROJECT.bat truoc.
    pause
    exit /b 1
)

if not exist "cloudflared.exe" (
    echo [LOI] Khong tim thay cloudflared.exe.
    pause
    exit /b 1
)

echo Dang khoi dong he thong va tao link Online...
".venv\Scripts\python.exe" scripts\run_online.py

echo.
echo He thong da dung.
pause
endlocal

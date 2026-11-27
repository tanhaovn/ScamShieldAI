@echo off
setlocal
title Scam Detector - Online Public Mode
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [LOI] Du an chua duoc cai dat moi truong Python.
    echo Hay nhap dup SETUP_PROJECT.bat truoc.
    pause
    exit /b 1
)

echo Dang khoi dong he thong va tao link Online...
".venv\Scripts\python.exe" scripts\run_online.py

echo.
echo He thong da dung.
pause
endlocal

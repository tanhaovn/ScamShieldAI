@echo off
title Scam Detector - Frontend
cd /d "%~dp0frontend-react"

where npm.cmd >nul 2>nul
if errorlevel 1 (
    echo [LOI] Khong tim thay Node.js/npm.
    echo Hay cai Node.js LTS roi chay lai SETUP_PROJECT.bat.
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo [LOI] Chua cai thu vien frontend.
    echo Hay chay SETUP_PROJECT.bat truoc.
    pause
    exit /b 1
)

echo Dang khoi dong Frontend tai http://127.0.0.1:5173
echo.
npm.cmd run dev

echo.
echo Frontend da dung hoac gap loi.
pause

@echo off
setlocal
title Scam Detector - Setup Project
cd /d "%~dp0"

echo ========================================
echo   CAI DAT DU AN SCAM DETECTOR LAN DAU
echo ========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [LOI] Khong tim thay Python.
    echo Hay cai Python 3.12 va chon Add Python to PATH.
    pause
    exit /b 1
)

where npm.cmd >nul 2>nul
if errorlevel 1 (
    echo [LOI] Khong tim thay Node.js/npm.
    echo Hay cai Node.js LTS truoc.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [1/4] Dang tao moi truong Python .venv...
    python -m venv .venv
    if errorlevel 1 goto :setup_error
) else (
    echo [1/4] Da co moi truong Python .venv.
)

echo [2/4] Dang cai thu vien Python...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :setup_error

echo [3/4] Dang cai thu vien React...
pushd frontend-react
npm.cmd install
if errorlevel 1 (
    popd
    goto :setup_error
)
popd

echo [4/4] Kiem tra cau hinh...
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo Da tao file .env tu .env.example.
    echo Neu dung MySQL, hay sua DB_USER va DB_PASSWORD trong .env.
)

echo.
echo ========================================
echo   CAI DAT HOAN TAT
echo ========================================
echo Tu lan sau chi can nhap dup START_PROJECT.bat
echo.
pause
exit /b 0

:setup_error
echo.
echo [LOI] Cai dat khong thanh cong. Xem thong bao phia tren.
pause
exit /b 1

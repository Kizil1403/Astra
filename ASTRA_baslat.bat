@echo off
chcp 65001 >nul
title ASTRA - Murettebat Saglik Sistemi
cd /d "%~dp0"

REM --- Python kurulu mu? ---
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo  Python bulunamadi.
    echo  python.org adresinden Python indirip kurun.
    echo  Kurulumda "Add python.exe to PATH" kutusunu isaretlemeyi unutmayin.
    echo.
    pause
    exit /b
)

REM --- Ilk acilista gerekli paketleri bir kez yukle ---
if not exist ".kurulum_tamam" (
    echo.
    echo  ASTRA ilk kez aciliyor. Gerekli paketler yukleniyor, bu birkac dakika surebilir...
    echo.
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo  Paketler yuklenemedi. Internet baglantinizi kontrol edip tekrar deneyin.
        pause
        exit /b
    )
    echo tamam> ".kurulum_tamam"
)

REM --- Uygulamayi baslat (tarayicida kendiliginden acilir) ---
echo.
echo  ASTRA baslatiliyor... Kapatmak icin bu pencereyi kapatin.
echo.
python -m streamlit run main.py --server.headless false
pause

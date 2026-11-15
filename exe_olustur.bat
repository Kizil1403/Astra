@echo off
chcp 65001 >nul
title ASTRA.exe olusturuluyor
cd /d "%~dp0"

echo.
echo  ============================================================
echo   ASTRA.exe olusturuluyor. Bu islem 5-15 dakika surebilir.
echo   Bu islemi SADECE SIZ bir kez yaparsiniz; olusan klasoru
echo   Python'u olmayan herkes kullanabilir.
echo  ============================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo  Python bulunamadi. Exe olusturmak icin bu bilgisayarda Python gerekli.
    pause
    exit /b
)

echo  [1/3] Gerekli paketler yukleniyor...
python -m pip install --upgrade pyinstaller -r requirements.txt
if errorlevel 1 goto hata

echo.
echo  [2/3] Uygulama paketleniyor...
python -m PyInstaller --noconfirm --clean --onedir --name ASTRA --icon "assets\astra.ico" ^
  --collect-all streamlit ^
  --collect-all plotly ^
  --collect-all openpyxl ^
  --collect-all deep_translator ^
  --collect-all google.genai ^
  --copy-metadata streamlit ^
  --copy-metadata google-genai ^
  --copy-metadata pandas ^
  --copy-metadata numpy ^
  --hidden-import sqlite3 ^
  --add-data "main.py;." ^
  --add-data "ayarlar.py;." ^
  --add-data "arayuz.py;." ^
  --add-data "ceviri.py;." ^
  --add-data "sozluk.py;." ^
  --add-data "veritabani.py;." ^
  --add-data "saat_simulatoru.py;." ^
  --add-data "saglik_motoru.py;." ^
  --add-data "vucut_cizimi.py;." ^
  --add-data "xray.py;." ^
  --add-data "grafikler.py;." ^
  --add-data "monitor.py;." ^
  --add-data "yapay_zeka.py;." ^
  --add-data "dongu_takibi.py;." ^
  --add-data "sayfalar;sayfalar" ^
  --add-data "assets;assets" ^
  --add-data ".streamlit;.streamlit" ^
  astra_masaustu.py > exe_olusturma_kaydi.txt 2>&1
if errorlevel 1 goto hata

echo.
echo  [3/3] Okuma notu ekleniyor...
copy /y "BENI_OKU_EXE.txt" "dist\ASTRA\BENI_OKU.txt" >nul

echo.
echo  ============================================================
echo   TAMAM! Uygulamaniz hazir:  dist\ASTRA\ASTRA.exe
echo.
echo   Paylasmak icin "dist\ASTRA" klasorunun TAMAMINI zip yapin.
echo   (Sadece ASTRA.exe yetmez; yanindaki _internal klasoru da gerekli.)
echo  ============================================================
explorer "dist\ASTRA"
pause
exit /b

:hata
echo.
echo  Bir hata olustu. Ayrintilar: exe_olusturma_kaydi.txt
echo  Bu dosyanin son satirlarini Claude'a gonderin.
pause

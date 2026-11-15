@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  Paylasim icin temizlik: kisisel verileriniz ve Gemini anahtariniz silinecek.
echo  (astronot_saglik.db, kayitlar klasoru)
echo.
set /p ONAY=Devam etmek icin E yazip Enter'a basin: 
if /i not "%ONAY%"=="E" (
    echo Iptal edildi.
    pause
    exit /b
)
if exist "astronot_saglik.db" del /q "astronot_saglik.db"
if exist "kayitlar" rd /s /q "kayitlar"
if exist ".kurulum_tamam" del /q ".kurulum_tamam"
echo.
echo  Tamam. Klasoru simdi zip yapip paylasabilirsiniz.
pause

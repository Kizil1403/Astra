@echo off
chcp 65001 >nul
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$k = (New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop') + '\ASTRA.lnk'); $k.TargetPath = '%~dp0ASTRA_baslat.bat'; $k.WorkingDirectory = '%~dp0'; $k.IconLocation = '%~dp0assets\astra.ico'; $k.Description = 'ASTRA Murettebat Saglik Sistemi'; $k.Save()"
if errorlevel 1 (
    echo Kisayol olusturulamadi.
) else (
    echo Masaustune ASTRA kisayolu eklendi. Artik ona cift tiklayarak acabilirsiniz.
)
pause

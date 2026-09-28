@echo off
cd /d "%~dp0"
echo ===================================================
echo [*] Whisper Pill Pro 2.0 - Paket-Updater
echo ===================================================
echo.
echo [*] Aktualisiere faster-whisper, ctranslate2 und sounddevice...
.\.venv\Scripts\python.exe -m pip install --upgrade faster-whisper ctranslate2 sounddevice numpy
echo.
echo [+] Update abgeschlossen!
pause

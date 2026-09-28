@echo off
cd /d "%~dp0"
echo [*] Starte Whisper Pill Pro 2.0...
start "" ".\.venv\Scripts\python.exe" "whisper_pill.py"
exit

@echo off
cd /d "%~dp0"

if not exist ".\.venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .\.venv\Scripts\python.exe
    pause
    exit /b 1
)

.\.venv\Scripts\python.exe aleapp.py %*


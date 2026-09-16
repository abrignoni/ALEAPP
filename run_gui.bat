@echo off
cd /d "%~dp0"
echo ===================================================
echo Starting ALEAPP (Android Logs Events ^& Protobuf Parser)
echo ===================================================

if not exist ".\.venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .\.venv\Scripts\python.exe
    pause
    exit /b 1
)

.\.venv\Scripts\python.exe aleappGUI.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] ALEAPP GUI exited with error code %ERRORLEVEL%.
    pause
)


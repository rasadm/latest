@echo off
echo Starting Settings Management Dashboard...
echo Checking dependencies...
python -c "import tkinter, requests, json, os, uuid, datetime" 2>nul
if errorlevel 1 (
    echo Error: Missing required dependencies
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo Launching Settings Dashboard...
python settings_dashboard.py
pause 
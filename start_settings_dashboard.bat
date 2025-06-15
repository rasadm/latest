@echo off
echo ==========================================
echo Starting Settings Dashboard
echo ==========================================

REM Set the Python path to include the current directory
set PYTHONPATH=%~dp0

REM Start the settings dashboard
echo Starting Settings Dashboard...
python dashboards/settings_dashboard.py

pause 
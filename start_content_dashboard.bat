@echo off
echo ==========================================
echo Starting Content Management Dashboard
echo ==========================================

REM Set the Python path to include the current directory
set PYTHONPATH=%~dp0

REM Start the content dashboard
echo Starting Content Dashboard...
python dashboards/content_dashboard.py

pause 
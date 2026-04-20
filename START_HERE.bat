@echo off
echo ========================================
echo    CLASSWAVE EMAIL SERVICE STARTUP
echo ========================================
echo.
echo This script will:
echo 1. Check if email service is running
echo 2. Start it automatically if needed
echo 3. Show current email status
echo.
echo Run this every time you open the project!
echo.
pause

echo Starting auto-start script...
python auto_start_email_service.py

echo.
echo ========================================
echo Email service startup complete!
echo ========================================
echo.
echo Quick commands:
echo - Check status: python email_service_status.py
echo - Live monitor: python email_service_dashboard.py
echo - Manual start: python start_continuous_email_service.py
echo.
pause
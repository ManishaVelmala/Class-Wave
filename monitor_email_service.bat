@echo off
echo 📊 EMAIL SERVICE MONITORING TOOLS
echo ==================================
echo.
echo Choose monitoring option:
echo 1. Live Dashboard (real-time updates)
echo 2. Health Check (single check)
echo 3. Service Status (detailed report)
echo.
set /p choice="Enter choice (1, 2, or 3): "

if "%choice%"=="1" (
    echo Starting live dashboard...
    python email_service_dashboard.py
) else if "%choice%"=="2" (
    echo Running health check...
    echo 1 | python simple_service_monitor.py
    pause
) else if "%choice%"=="3" (
    echo Getting service status...
    python email_service_status.py
    pause
) else (
    echo Invalid choice. Running health check...
    echo 1 | python simple_service_monitor.py
    pause
)
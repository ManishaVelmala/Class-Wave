@echo off
title ClassWave 30-Second Email Service
echo ========================================
echo  ClassWave 30-Second Email Service
echo ========================================
echo.
echo Starting continuous email monitoring...
echo Maximum delay: 30 seconds
echo Perfect timing for all time preferences
echo.
echo Service will restart automatically if stopped
echo Press Ctrl+C to stop permanently
echo.

:start
python start_continuous_email_service.py
echo.
echo Service stopped. Restarting in 10 seconds...
echo Press Ctrl+C now to stop permanently
timeout /t 10 /nobreak >nul
goto start
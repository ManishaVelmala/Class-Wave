@echo off
title ClassWave Automatic Service
echo Starting ClassWave Automatic Service...
echo Emails will be sent automatically
echo Close this window to stop the service
echo.

:loop
python start_full_automation.py
echo Service stopped. Restarting in 10 seconds...
timeout /t 10 /nobreak >nul
goto loop
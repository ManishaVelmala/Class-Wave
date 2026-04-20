@echo off
echo [%date% %time%] Running ClassWave Email Service...
cd /d "%~dp0"
python manage.py send_real_daily_digests
echo [%date% %time%] Email service completed
echo.

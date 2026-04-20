@echo off
echo Running ClassWave Email Service...
cd /d "%~dp0"
python manage.py send_real_daily_digests
echo Email service completed at %date% %time%

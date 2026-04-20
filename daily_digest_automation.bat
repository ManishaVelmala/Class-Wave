@echo off
REM ClassWave Daily Digest Automation
REM This runs every day at 6:00 AM to generate and send daily digests

echo ClassWave Daily Digest Service Starting...
echo Date: %date%
echo Time: %time%

cd /d "C:\Users\velma\OneDrive\Desktop\Lecturebuzz"

echo Generating today's digests...
python generate_todays_digest.py

echo ✅ Daily digest service completed
echo.

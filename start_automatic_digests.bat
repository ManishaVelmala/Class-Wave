@echo off
REM ClassWave Automatic Daily Digest Daemon
REM This runs continuously in the background and automatically generates/sends digests

echo 🤖 Starting ClassWave Automatic Digest System...
cd /d "C:\Users\velma\OneDrive\Desktop\Lecturebuzz"

echo 📅 Starting automatic daily digest daemon...
echo This will run continuously and automatically:
echo   - Generate daily digests for all students
echo   - Send emails at student preferred times
echo   - No manual intervention needed
echo.
echo Press Ctrl+C to stop the daemon
echo.

python manage.py auto_daily_digests --daemon
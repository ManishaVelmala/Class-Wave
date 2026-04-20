@echo off
REM Daily Digest Automation Script for ClassWave
REM This script sends daily digests to all students automatically

echo Starting ClassWave Daily Digest Generation...
cd /d "C:\Users\velma\OneDrive\Desktop\Lecturebuzz"

echo Generating daily digests for all students...
python generate_todays_digest.py

echo Daily digest generation completed!
echo Check student_gmail_emails folder for generated emails.

REM Optional: Also run the official command
REM python manage.py send_daily_digests

pause
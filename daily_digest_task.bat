@echo off
cd /d "C:\Users\velma\OneDrive\Desktop\Lecturebuzz"
python manage.py refresh_todays_digests
python manage.py send_due_emails
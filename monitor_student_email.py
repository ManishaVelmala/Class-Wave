#!/usr/bin/env python3
import os, sys, django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.utils import timezone
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def monitor_student(username):
    try:
        student = User.objects.get(username=username)
        pref = DailyDigestPreference.objects.get(student=student)
        
        india_now = timezone.now() + timedelta(hours=5, minutes=30)
        current_time = india_now.time()
        
        print(f"MONITORING: {username}")
        print(f"Email: {student.email}")
        print(f"Preference: {pref.digest_time.strftime('%I:%M %p')} India")
        print(f"Current: {current_time.strftime('%I:%M %p')} India")
        print(f"Enabled: {'Yes' if pref.is_enabled else 'No'}")
        print(f"Due: {'Yes' if current_time >= pref.digest_time else 'No'}")
        
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=india_now.date()
        ).first()
        
        if digest:
            print(f"Digest: {'Sent' if digest.is_sent else 'Pending'}")
            if digest.is_sent and digest.sent_at:
                india_sent_time = digest.sent_at + timedelta(hours=5, minutes=30)
                print(f"Sent at: {india_sent_time.strftime('%I:%M %p India')}")
        else:
            print(f"Digest: Not found")
            
    except User.DoesNotExist:
        print(f"Error: User '{username}' not found")
    except DailyDigestPreference.DoesNotExist:
        print(f"Error: No preference set for {username}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        monitor_student(sys.argv[1])
    else:
        print("Usage: python monitor_student_email.py <username>")
        print("Example: python monitor_student_email.py Vaishnavi")

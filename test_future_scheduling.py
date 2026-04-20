#!/usr/bin/env python
"""
Test future email scheduling by creating test reminders for specific times
"""

import os
import django
from datetime import date, time, datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference
from django.core.mail import send_mail
from django.conf import settings

def test_future_scheduling():
    print("⏰ TESTING FUTURE EMAIL SCHEDULING")
    print("=" * 60)
    
    now = datetime.now()
    
    # Create test times in the near future (next few minutes)
    test_times = [
        now + timedelta(minutes=2),   # 2 minutes from now
        now + timedelta(minutes=5),   # 5 minutes from now
        now + timedelta(minutes=8),   # 8 minutes from now
    ]
    
    students = User.objects.filter(user_type='student')[:3]  # Test with first 3 students
    
    print(f"🧪 Creating test reminders for future delivery:")
    print(f"⏰ Current time: {now.strftime('%H:%M:%S')}")
    print()
    
    for i, student in enumerate(students):
        if i < len(test_times):
            test_time = test_times[i]
            
            # Create test reminder
            test_message = f"""⏰ Future Scheduling Test - {student.username}

Hello {student.username}!

This is a FUTURE SCHEDULING test to verify that emails are sent at specific times.

🎯 Test Details:
   • Scheduled for: {test_time.strftime('%H:%M:%S')}
   • Current time when created: {now.strftime('%H:%M:%S')}
   • Your email: {student.email}

If you receive this email at approximately {test_time.strftime('%H:%M')}, 
the time-based scheduling system is working perfectly! ⏰

This proves that:
✅ Emails can be scheduled for future delivery
✅ System sends emails at exact specified times
✅ You don't need to be logged in to receive emails
✅ The middleware is working correctly

Best regards,
ClassWave Team 🔔

---
Automated test message - Future Scheduling Verification
"""
            
            reminder = Reminder.objects.create(
                student=student,
                schedule=None,
                reminder_time=test_time,
                message=test_message,
                reminder_type='future_test',
                is_sent=False
            )
            
            minutes_until = int((test_time - now).total_seconds() / 60)
            print(f"👤 {student.username}:")
            print(f"   📧 Email: {student.email}")
            print(f"   ⏰ Scheduled for: {test_time.strftime('%H:%M:%S')}")
            print(f"   ⏳ Will be sent in: {minutes_until} minutes")
            print()
    
    print(f"🚀 TEST SETUP COMPLETE!")
    print(f"📧 {len(students)} test emails scheduled for the next 8 minutes")
    
    print(f"\n🎯 TO SEE THE TEST IN ACTION:")
    print(f"   1. Run: python manage.py runserver")
    print(f"   2. Keep the server running")
    print(f"   3. Watch the console - middleware checks every 5 minutes")
    print(f"   4. Students will receive emails at their scheduled times")
    
    print(f"\n⏰ EXPECTED DELIVERY TIMES:")
    for i, student in enumerate(students):
        if i < len(test_times):
            print(f"   👤 {student.username}: {test_times[i].strftime('%H:%M:%S')}")
    
    print(f"\n📋 VERIFICATION:")
    print(f"   • Check Gmail inboxes at the scheduled times")
    print(f"   • Emails should arrive within 1-5 minutes of scheduled time")
    print(f"   • This proves the time preference system works perfectly!")
    
    # Show how to check status
    print(f"\n🔍 TO CHECK STATUS:")
    print(f"   Run: python check_scheduled_tests.py")

if __name__ == "__main__":
    test_future_scheduling()
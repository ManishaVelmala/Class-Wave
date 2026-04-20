#!/usr/bin/env python
"""
Check the status of scheduled test emails
"""

import os
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from reminders.models import Reminder

def check_scheduled_tests():
    print("📋 CHECKING SCHEDULED TEST EMAIL STATUS")
    print("=" * 60)
    
    now = datetime.now()
    print(f"⏰ Current time: {now.strftime('%H:%M:%S')}")
    
    # Check test messages
    test_reminders = Reminder.objects.filter(
        reminder_type__in=['future_test', 'test_message']
    ).order_by('reminder_time')
    
    if not test_reminders.exists():
        print("ℹ️ No test reminders found")
        return
    
    print(f"\n📧 TEST EMAIL STATUS:")
    
    pending_count = 0
    sent_count = 0
    overdue_count = 0
    
    for reminder in test_reminders:
        scheduled_time = reminder.reminder_time.replace(tzinfo=None)
        time_diff = (scheduled_time - now).total_seconds()
        
        print(f"\n👤 {reminder.student.username}:")
        print(f"   📧 Email: {reminder.student.email}")
        print(f"   ⏰ Scheduled: {scheduled_time.strftime('%H:%M:%S')}")
        
        if reminder.is_sent:
            print(f"   ✅ Status: SENT")
            print(f"   📬 Delivered to Gmail inbox")
            sent_count += 1
        elif time_diff > 0:
            minutes = int(time_diff / 60)
            print(f"   ⏳ Status: PENDING (in {minutes} minutes)")
            pending_count += 1
        else:
            minutes_overdue = int(abs(time_diff) / 60)
            print(f"   🚨 Status: OVERDUE (by {minutes_overdue} minutes)")
            print(f"   💡 Should be sent on next middleware check")
            overdue_count += 1
    
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Sent: {sent_count}")
    print(f"   ⏳ Pending: {pending_count}")
    print(f"   🚨 Overdue: {overdue_count}")
    
    if overdue_count > 0:
        print(f"\n🚀 TO SEND OVERDUE EMAILS:")
        print(f"   Run: python manage.py runserver")
        print(f"   Visit: http://127.0.0.1:8000")
        print(f"   Middleware will send overdue emails immediately")
    
    if pending_count > 0:
        print(f"\n⏰ PENDING EMAILS:")
        print(f"   Keep server running - emails will be sent automatically")
        print(f"   Middleware checks every 5 minutes")
    
    if sent_count > 0:
        print(f"\n🎉 SUCCESS:")
        print(f"   {sent_count} test emails have been delivered!")
        print(f"   Check Gmail inboxes to verify receipt")

if __name__ == "__main__":
    check_scheduled_tests()
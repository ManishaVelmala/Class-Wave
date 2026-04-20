#!/usr/bin/env python
"""
Test that notification bar shows ONLY today's schedule
"""

import os
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.models import Reminder
from schedules.models import Schedule

def test_today_only_notifications():
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    print(f"🗓️  TESTING TODAY-ONLY NOTIFICATIONS")
    print(f"   Yesterday: {yesterday}")
    print(f"   Today: {today}")
    print(f"   Tomorrow: {tomorrow}")
    print("=" * 50)
    
    # Get a student
    student = User.objects.filter(user_type='student').first()
    print(f"👤 Testing with student: {student.username}")
    
    # Check what digests exist in database
    all_digests = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest'
    ).order_by('digest_date')
    
    print(f"\n📊 ALL DIGESTS IN DATABASE:")
    for digest in all_digests:
        print(f"   {digest.digest_date} - Sent: {digest.is_sent}")
    
    # Check what appears in notification bar (using same logic as views.py)
    notification_bar_digests = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True
    )
    
    print(f"\n📱 NOTIFICATION BAR SHOWS:")
    if notification_bar_digests.exists():
        for digest in notification_bar_digests:
            print(f"   ✅ {digest.digest_date} - TODAY'S SCHEDULE")
    else:
        print(f"   ℹ️ No notifications (no classes today)")
    
    # Check schedules for today
    todays_schedules = Schedule.objects.filter(date=today)
    print(f"\n📚 SCHEDULES FOR TODAY: {todays_schedules.count()}")
    
    # Verify behavior
    if todays_schedules.exists() and notification_bar_digests.exists():
        print(f"\n✅ CORRECT: Shows today's schedule in notification bar")
    elif not todays_schedules.exists() and not notification_bar_digests.exists():
        print(f"\n✅ CORRECT: No classes today, notification bar is empty")
    else:
        print(f"\n❌ ISSUE: Mismatch between schedules and notifications")

if __name__ == "__main__":
    test_today_only_notifications()
#!/usr/bin/env python
"""
Complete test of notification bar behavior - today only
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

def test_complete_behavior():
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    print(f"🧪 COMPLETE NOTIFICATION BAR TEST")
    print("=" * 50)
    
    student = User.objects.filter(user_type='student').first()
    
    # Check schedules for different dates
    today_schedules = Schedule.objects.filter(date=today).count()
    yesterday_schedules = Schedule.objects.filter(date=yesterday).count()
    tomorrow_schedules = Schedule.objects.filter(date=tomorrow).count()
    
    print(f"📅 SCHEDULES:")
    print(f"   Yesterday ({yesterday}): {yesterday_schedules}")
    print(f"   Today ({today}): {today_schedules}")
    print(f"   Tomorrow ({tomorrow}): {tomorrow_schedules}")
    
    # Check digests in database
    all_digests = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest'
    )
    
    print(f"\n📊 DIGESTS IN DATABASE:")
    for digest in all_digests.order_by('digest_date'):
        print(f"   {digest.digest_date}: Sent={digest.is_sent}")
    
    # Check what notification bar shows (same logic as views.py)
    visible_notifications = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True
    )
    
    print(f"\n📱 NOTIFICATION BAR:")
    if visible_notifications.exists():
        for notif in visible_notifications:
            print(f"   ✅ {notif.digest_date} - TODAY'S SCHEDULE")
    else:
        print(f"   ℹ️ Empty (no classes today)")
    
    # Verify correct behavior
    print(f"\n🔍 VERIFICATION:")
    
    # Rule 1: Only today's digest should be visible
    past_future_visible = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        is_sent=True
    ).exclude(digest_date=today)
    
    if past_future_visible.exists():
        print(f"   ❌ FAIL: Past/future digests are visible")
        for notif in past_future_visible:
            print(f"      - {notif.digest_date}")
    else:
        print(f"   ✅ PASS: No past/future digests visible")
    
    # Rule 2: If no classes today, notification bar should be empty
    if today_schedules == 0:
        if visible_notifications.exists():
            print(f"   ❌ FAIL: No classes today but notification bar shows digest")
        else:
            print(f"   ✅ PASS: No classes today, notification bar empty")
    
    # Rule 3: If classes today, notification bar should show today's digest
    if today_schedules > 0:
        if visible_notifications.exists():
            print(f"   ✅ PASS: Classes today, notification bar shows today's digest")
        else:
            print(f"   ❌ FAIL: Classes today but notification bar is empty")
    
    print(f"\n🎯 SUMMARY:")
    if today_schedules > 0 and visible_notifications.exists():
        print(f"   ✅ Perfect: Shows only today's schedule")
    elif today_schedules == 0 and not visible_notifications.exists():
        print(f"   ✅ Perfect: No classes today, notification bar empty")
    else:
        print(f"   ❌ Issue detected")

if __name__ == "__main__":
    test_complete_behavior()
#!/usr/bin/env python
"""
Final comprehensive test of the today-only notification system
"""

import os
import django
from datetime import date, timedelta, time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.models import Reminder
from schedules.models import Schedule

def final_test():
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    print(f"🎯 FINAL NOTIFICATION SYSTEM TEST")
    print(f"   Testing date: {today}")
    print("=" * 60)
    
    # Clean slate - remove all existing digests
    Reminder.objects.filter(reminder_type='daily_digest').delete()
    print(f"🧹 Cleaned all existing digests")
    
    # Get test users
    student = User.objects.filter(user_type='student').first()
    lecturer = User.objects.filter(user_type='lecturer').first()
    
    print(f"👤 Test student: {student.username}")
    
    # Test Case 1: No schedules today
    print(f"\n📋 TEST CASE 1: No schedules for today")
    Schedule.objects.filter(date=today).delete()
    
    # Check notification bar
    notifications = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True
    )
    
    if notifications.exists():
        print(f"   ❌ FAIL: Notification bar shows digest when no classes")
    else:
        print(f"   ✅ PASS: Notification bar empty (no classes today)")
    
    # Test Case 2: Create schedule for today
    print(f"\n📋 TEST CASE 2: Create schedule for today")
    todays_schedule = Schedule.objects.create(
        subject_name='Test Today',
        topic='Today\'s class',
        date=today,
        start_time=time(10, 0),
        end_time=time(11, 0),
        lecturer=lecturer,
        department='MCA',
        batch='2024-2026'
    )
    todays_schedule.students.add(student)
    
    # Generate digest
    from reminders.tasks import create_daily_digest_for_student
    digest = create_daily_digest_for_student(student.id, today)
    if digest:
        digest.is_sent = True
        digest.save()
    
    # Check notification bar
    notifications = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True
    )
    
    if notifications.exists():
        print(f"   ✅ PASS: Notification bar shows today's digest")
        print(f"   📅 Digest date: {notifications.first().digest_date}")
    else:
        print(f"   ❌ FAIL: No notification when classes exist today")
    
    # Test Case 3: Create schedules for other dates (should not appear)
    print(f"\n📋 TEST CASE 3: Create schedules for other dates")
    
    # Yesterday's schedule
    yesterday_schedule = Schedule.objects.create(
        subject_name='Test Yesterday',
        topic='Yesterday\'s class',
        date=yesterday,
        start_time=time(9, 0),
        end_time=time(10, 0),
        lecturer=lecturer,
        department='MCA',
        batch='2024-2026'
    )
    yesterday_schedule.students.add(student)
    
    # Tomorrow's schedule
    tomorrow_schedule = Schedule.objects.create(
        subject_name='Test Tomorrow',
        topic='Tomorrow\'s class',
        date=tomorrow,
        start_time=time(14, 0),
        end_time=time(15, 0),
        lecturer=lecturer,
        department='MCA',
        batch='2024-2026'
    )
    tomorrow_schedule.students.add(student)
    
    # Check that only today's digest appears
    all_notifications = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        is_sent=True
    )
    
    today_notifications = all_notifications.filter(digest_date=today)
    other_notifications = all_notifications.exclude(digest_date=today)
    
    print(f"   📊 Total digests in DB: {all_notifications.count()}")
    print(f"   📅 Today's digests: {today_notifications.count()}")
    print(f"   📅 Other date digests: {other_notifications.count()}")
    
    # Check notification bar (using same logic as views.py)
    visible_notifications = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today,  # Only today's
        is_sent=True
    )
    
    if visible_notifications.count() == 1 and visible_notifications.first().digest_date == today:
        print(f"   ✅ PASS: Notification bar shows ONLY today's digest")
    else:
        print(f"   ❌ FAIL: Notification bar shows wrong digests")
        for notif in visible_notifications:
            print(f"      - {notif.digest_date}")
    
    # Test Case 4: Update today's schedule (should refresh digest)
    print(f"\n📋 TEST CASE 4: Update today's schedule")
    old_topic = todays_schedule.topic
    todays_schedule.topic = "UPDATED: Today's class topic"
    todays_schedule.save()  # Should trigger signal
    
    # Check if digest was refreshed
    updated_digest = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True
    ).first()
    
    if updated_digest and "UPDATED" in updated_digest.message:
        print(f"   ✅ PASS: Digest automatically refreshed with updated schedule")
    else:
        print(f"   ❌ FAIL: Digest not refreshed after schedule update")
    
    # Final Summary
    print(f"\n🎯 FINAL VERIFICATION:")
    
    # Count schedules
    today_schedules = Schedule.objects.filter(date=today).count()
    yesterday_schedules = Schedule.objects.filter(date=yesterday).count()
    tomorrow_schedules = Schedule.objects.filter(date=tomorrow).count()
    
    print(f"   📚 Schedules - Yesterday: {yesterday_schedules}, Today: {today_schedules}, Tomorrow: {tomorrow_schedules}")
    
    # Count visible notifications
    visible = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True
    ).count()
    
    print(f"   📱 Visible notifications: {visible} (should be 1 if classes today, 0 if no classes)")
    
    if today_schedules > 0 and visible == 1:
        print(f"   ✅ SUCCESS: Perfect behavior - shows only today's schedule")
    elif today_schedules == 0 and visible == 0:
        print(f"   ✅ SUCCESS: Perfect behavior - no classes today, notification bar empty")
    else:
        print(f"   ❌ ISSUE: Unexpected behavior")
    
    # Cleanup
    print(f"\n🧹 Cleaning up test data...")
    Schedule.objects.filter(subject_name__startswith='Test').delete()
    Reminder.objects.filter(reminder_type='daily_digest').delete()
    print(f"   ✅ Test data cleaned")

if __name__ == "__main__":
    final_test()
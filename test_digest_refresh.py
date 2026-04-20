#!/usr/bin/env python
"""
Test if daily digest gets refreshed when schedules are updated
"""

import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from schedules.models import Schedule
from reminders.models import Reminder

def test_digest_refresh():
    today = date.today()
    print(f"🗓️  TESTING DIGEST REFRESH FOR: {today}")
    print("=" * 50)
    
    # Get a schedule for today
    todays_schedule = Schedule.objects.filter(date=today).first()
    if not todays_schedule:
        print("❌ No schedule found for today")
        return
    
    print(f"📚 Found schedule: {todays_schedule.subject_name}")
    print(f"   Current topic: {todays_schedule.topic}")
    
    # Get a student from this schedule
    student = todays_schedule.students.first()
    if not student:
        print("❌ No students found for this schedule")
        return
    
    print(f"👤 Testing with student: {student.username}")
    
    # Check current digest
    current_digest = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).first()
    
    if current_digest:
        print(f"\n📧 Current digest message preview:")
        print(current_digest.message[:200] + "...")
    
    # Update the schedule topic
    old_topic = todays_schedule.topic
    new_topic = f"UPDATED: {old_topic}"
    
    print(f"\n🔄 Updating schedule topic...")
    print(f"   From: {old_topic}")
    print(f"   To: {new_topic}")
    
    todays_schedule.topic = new_topic
    todays_schedule.save()  # This should trigger the signal
    
    # Check if digest was refreshed
    refreshed_digest = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).first()
    
    if refreshed_digest:
        print(f"\n📧 Refreshed digest message preview:")
        print(refreshed_digest.message[:200] + "...")
        
        if new_topic in refreshed_digest.message:
            print("✅ SUCCESS: Digest was refreshed with updated topic!")
        else:
            print("❌ FAILED: Digest still contains old topic")
    else:
        print("❌ FAILED: No digest found after update")
    
    # Restore original topic
    todays_schedule.topic = old_topic
    todays_schedule.save()
    print(f"\n🔄 Restored original topic: {old_topic}")

if __name__ == "__main__":
    test_digest_refresh()
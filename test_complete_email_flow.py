#!/usr/bin/env python
"""
Test script to demonstrate the complete email flow:
1. Student receives daily digest with scheduled reminders
2. Schedule gets updated
3. Student receives update notification email
"""

import os
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from schedules.models import Schedule
from reminders.tasks import create_daily_digest_for_student

def test_complete_email_flow():
    print("🔄 TESTING COMPLETE EMAIL FLOW")
    print("=" * 50)
    
    # Step 1: Find a student with schedules
    students = User.objects.filter(user_type='student')
    if not students.exists():
        print("❌ No students found!")
        return
    
    student = students.first()
    print(f"👤 Testing with student: {student.username} ({student.email})")
    
    # Step 2: Find schedules for this student
    tomorrow = date.today() + timedelta(days=1)
    schedules = Schedule.objects.filter(students=student, date=tomorrow)
    
    if not schedules.exists():
        print(f"📅 No schedules found for {tomorrow}")
        # Try today
        today = date.today()
        schedules = Schedule.objects.filter(students=student, date=today)
        if schedules.exists():
            tomorrow = today
            print(f"📅 Using today's schedules: {today}")
        else:
            print("❌ No schedules found for testing!")
            return
    
    print(f"📚 Found {schedules.count()} schedules for {tomorrow}")
    
    # Step 3: Generate daily digest (simulates scheduled reminder email)
    print("\n🔄 STEP 1: Generating Daily Digest Email...")
    digest = create_daily_digest_for_student(student.id, tomorrow)
    
    if digest:
        print(f"✅ Daily digest created!")
        print(f"   📧 Email would be sent at: {digest.reminder_time}")
        print(f"   📝 Message preview: {digest.message[:100]}...")
    else:
        print("❌ Failed to create daily digest!")
        return
    
    # Step 4: Update one of the schedules (simulates lecturer making changes)
    test_schedule = schedules.first()
    old_topic = test_schedule.topic
    new_topic = f"UPDATED: {old_topic}"
    
    print(f"\n🔄 STEP 2: Updating Schedule...")
    print(f"   📚 Schedule: {test_schedule.subject_name}")
    print(f"   📝 Old Topic: {old_topic}")
    print(f"   📝 New Topic: {new_topic}")
    print(f"   👥 Students enrolled: {test_schedule.students.count()}")
    
    # This will trigger the signal and send update emails
    test_schedule.topic = new_topic
    test_schedule.save()
    
    print(f"\n✅ FLOW COMPLETE!")
    print(f"📧 Student {student.email} should have received:")
    print(f"   1. Daily digest email (scheduled)")
    print(f"   2. Update notification email (immediate)")
    
    return True

def check_email_configuration():
    """Check if email is properly configured"""
    from django.conf import settings
    
    print("🔧 CHECKING EMAIL CONFIGURATION")
    print("=" * 40)
    
    required_settings = [
        'EMAIL_BACKEND',
        'EMAIL_HOST',
        'EMAIL_PORT',
        'DEFAULT_FROM_EMAIL'
    ]
    
    for setting in required_settings:
        value = getattr(settings, setting, 'NOT SET')
        print(f"   {setting}: {value}")
    
    print()

if __name__ == "__main__":
    check_email_configuration()
    test_complete_email_flow()
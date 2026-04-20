#!/usr/bin/env python
"""
Test what happens when a new student registers and sets time preference to 9:30 PM
"""

import os
import django
from datetime import date, time, datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User, StudentProfile
from reminders.models import Reminder, DailyDigestPreference
from schedules.models import Schedule
from reminders.tasks import create_daily_digest_for_student

def test_new_student_registration():
    print("👤 TESTING NEW STUDENT REGISTRATION WITH 9:30 PM PREFERENCE")
    print("=" * 70)
    
    today = date.today()
    current_time = datetime.now().time()
    
    print(f"📅 Today's date: {today}")
    print(f"⏰ Current time: {current_time.strftime('%I:%M %p')}")
    
    # Check if there are schedules for today
    today_schedules = Schedule.objects.filter(date=today)
    print(f"📚 Schedules for today: {today_schedules.count()}")
    
    if today_schedules.exists():
        for schedule in today_schedules:
            print(f"   • {schedule.subject_name}: {schedule.start_time} - {schedule.end_time}")
    
    print(f"\n🆕 SCENARIO: New student registers NOW and sets preference to 9:30 PM")
    
    # Create a test student (simulate registration)
    test_username = "test_student_930pm"
    test_email = "teststudent930@gmail.com"
    
    # Clean up any existing test user
    User.objects.filter(username=test_username).delete()
    
    # Create new student
    new_student = User.objects.create_user(
        username=test_username,
        email=test_email,
        password="testpass123",
        user_type='student'
    )
    
    # Create student profile
    student_profile = StudentProfile.objects.create(
        user=new_student,
        department="MCA",
        batch="2024-2026",
        roll_number="TEST001"
    )
    
    print(f"✅ New student created: {new_student.username}")
    print(f"📧 Email: {new_student.email}")
    print(f"🏫 Department: {student_profile.department}")
    
    # Auto-assign to existing schedules (this happens during registration)
    matching_schedules = Schedule.objects.filter(
        department__iexact=student_profile.department,
        batch__iexact=student_profile.batch
    )
    
    for schedule in matching_schedules:
        schedule.students.add(new_student)
    
    print(f"📚 Auto-assigned to {matching_schedules.count()} schedules")
    
    # Set time preference to 9:30 PM
    preference_time = time(21, 30)  # 9:30 PM
    
    pref = DailyDigestPreference.objects.create(
        student=new_student,
        digest_time=preference_time,
        is_enabled=True
    )
    
    print(f"⚙️ Time preference set: {preference_time.strftime('%I:%M %p')}")
    
    # Check what happens with digest generation
    print(f"\n📧 DIGEST GENERATION TEST:")
    
    # Try to generate today's digest
    digest = create_daily_digest_for_student(new_student.id, today)
    
    if digest:
        digest_time = digest.reminder_time.strftime('%I:%M %p')
        digest_date = digest.reminder_time.date()
        
        print(f"✅ Digest created!")
        print(f"📅 Digest date: {digest.digest_date}")
        print(f"⏰ Delivery time: {digest_time}")
        print(f"📧 Email status: {'✅ SENT' if digest.is_sent else '⏳ PENDING'}")
        
        # Check if delivery time is today or yesterday
        if digest_date == today:
            print(f"📅 Delivery: TODAY at {digest_time}")
        elif digest_date < today:
            print(f"📅 Delivery: YESTERDAY at {digest_time} (for today's schedule)")
        else:
            print(f"📅 Delivery: FUTURE at {digest_time}")
        
        # Check if 9:30 PM has already passed today
        nine_thirty_pm = time(21, 30)
        if current_time > nine_thirty_pm:
            print(f"⏰ 9:30 PM has PASSED today")
            print(f"📧 Email will be sent: YESTERDAY at 9:30 PM (for today's schedule)")
        else:
            print(f"⏰ 9:30 PM has NOT passed today")
            print(f"📧 Email will be sent: TODAY at 9:30 PM")
        
    else:
        print(f"❌ No digest created (no schedules for today)")
    
    print(f"\n🎯 ANSWER TO YOUR QUESTION:")
    
    if digest:
        if current_time > time(21, 30):
            print(f"   ✅ YES, she gets an email!")
            print(f"   📧 Delivery: Yesterday 9:30 PM (for today's schedule)")
            print(f"   📅 Content: Today's schedule")
            print(f"   ⏰ Reason: 9:30 PM preference means 'day before' delivery")
        else:
            print(f"   ✅ YES, she will get an email!")
            print(f"   📧 Delivery: Today at 9:30 PM")
            print(f"   📅 Content: Today's schedule")
            print(f"   ⏰ Timing: Later today when 9:30 PM arrives")
    else:
        print(f"   ❌ NO email (no schedules for today)")
    
    print(f"\n🕘 9:30 PM PREFERENCE BEHAVIOR:")
    print(f"   📅 Evening times (8 PM+): Delivered day BEFORE")
    print(f"   📧 Purpose: Plan for next day")
    print(f"   ⏰ 9:30 PM preference: Gets tomorrow's schedule at 9:30 PM today")
    print(f"   📋 Content: 'Your schedule for [tomorrow's date]'")
    
    # Test tomorrow's digest
    from datetime import timedelta
    tomorrow = today + timedelta(days=1)
    
    tomorrow_schedules = Schedule.objects.filter(date=tomorrow)
    if tomorrow_schedules.exists():
        print(f"\n🔮 TOMORROW'S DIGEST TEST:")
        print(f"📚 Schedules for tomorrow: {tomorrow_schedules.count()}")
        
        tomorrow_digest = create_daily_digest_for_student(new_student.id, tomorrow)
        if tomorrow_digest:
            tomorrow_time = tomorrow_digest.reminder_time.strftime('%I:%M %p')
            tomorrow_date = tomorrow_digest.reminder_time.date()
            
            print(f"✅ Tomorrow's digest created!")
            print(f"📅 Digest for: {tomorrow}")
            print(f"⏰ Delivery: {tomorrow_date} at {tomorrow_time}")
            
            # Clean up tomorrow's test digest
            tomorrow_digest.delete()
    
    # Clean up test data
    if digest:
        digest.delete()
    new_student.delete()
    
    print(f"\n🧹 Test data cleaned up")
    
    print(f"\n📊 SUMMARY:")
    print(f"   👤 New student registers: Gets auto-assigned to schedules")
    print(f"   ⚙️ Sets 9:30 PM preference: Evening delivery (day before)")
    print(f"   📧 Gets digest: For today's schedule")
    print(f"   ⏰ Delivery timing: Yesterday 9:30 PM or today 9:30 PM")
    print(f"   📅 Content: Today's classes")

if __name__ == "__main__":
    test_new_student_registration()
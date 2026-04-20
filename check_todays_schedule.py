#!/usr/bin/env python
"""
Check what schedules exist for today (December 13, 2025)
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

def check_todays_schedule():
    today = date.today()
    print(f"🗓️  TODAY'S DATE: {today}")
    print("=" * 50)
    
    # Check schedules for today
    todays_schedules = Schedule.objects.filter(date=today)
    print(f"📚 Schedules for {today}: {todays_schedules.count()}")
    
    if todays_schedules.exists():
        print("\n📋 TODAY'S SCHEDULES:")
        for schedule in todays_schedules:
            print(f"   • {schedule.subject_name}")
            print(f"     Topic: {schedule.topic}")
            print(f"     Time: {schedule.start_time} - {schedule.end_time}")
            print(f"     Students: {schedule.students.count()}")
            print()
    else:
        print("ℹ️  No schedules found for today")
    
    # Check existing digests for today
    students = User.objects.filter(user_type='student')
    print(f"\n👥 STUDENTS: {students.count()}")
    
    for student in students:
        todays_digests = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        )
        
        print(f"\n👤 {student.username}:")
        print(f"   📧 Digests for {today}: {todays_digests.count()}")
        
        if todays_digests.exists():
            digest = todays_digests.first()
            print(f"   📧 Sent: {digest.is_sent}")
            print(f"   📖 Read: {digest.is_read}")
        else:
            print(f"   ⚠️  No digest created for today")
    
    # Check what dates have schedules
    print(f"\n📅 AVAILABLE SCHEDULE DATES:")
    all_dates = Schedule.objects.values_list('date', flat=True).distinct().order_by('date')
    for schedule_date in all_dates:
        count = Schedule.objects.filter(date=schedule_date).count()
        print(f"   {schedule_date}: {count} schedules")

if __name__ == "__main__":
    check_todays_schedule()
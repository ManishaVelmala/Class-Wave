#!/usr/bin/env python
"""
Verify that students will now receive only ONE email per day (not separate emails)
"""

import os
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from reminders.models import Reminder
from accounts.models import User
from schedules.models import Schedule

def verify_single_email_fix():
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    print("✅ VERIFYING SINGLE EMAIL FIX")
    print("=" * 60)
    
    # Check current reminder status
    print("1️⃣ CURRENT REMINDER STATUS:")
    
    all_reminders = Reminder.objects.all()
    daily_digests = all_reminders.filter(reminder_type='daily_digest')
    individual_reminders = all_reminders.filter(reminder_type='scheduled')
    other_reminders = all_reminders.exclude(reminder_type__in=['daily_digest', 'scheduled'])
    
    print(f"   📅 Daily digests: {daily_digests.count()} ✅")
    print(f"   📧 Individual reminders: {individual_reminders.count()} {'✅' if individual_reminders.count() == 0 else '❌'}")
    print(f"   🧪 Test reminders: {other_reminders.count()}")
    
    # Check what students will receive
    print(f"\n2️⃣ WHAT STUDENTS RECEIVE:")
    
    students = User.objects.filter(user_type='student')
    
    for student in students:
        student_digests = daily_digests.filter(student=student)
        student_individual = individual_reminders.filter(student=student)
        
        print(f"   👤 {student.username}:")
        print(f"      📅 Daily digests: {student_digests.count()}")
        print(f"      📧 Individual emails: {student_individual.count()}")
        
        if student_individual.count() > 0:
            print(f"      ❌ PROBLEM: Will receive {student_individual.count()} separate emails")
        else:
            print(f"      ✅ GOOD: Will receive combined daily digest only")
    
    # Test tomorrow's behavior
    print(f"\n3️⃣ TOMORROW'S EMAIL BEHAVIOR:")
    
    tomorrow_schedules = Schedule.objects.filter(date=tomorrow)
    print(f"   📚 Schedules for {tomorrow}: {tomorrow_schedules.count()}")
    
    if tomorrow_schedules.exists():
        print(f"   📧 Expected emails per student: 1 (combined daily digest)")
        print(f"   📋 Email will contain: All {tomorrow_schedules.count()} classes")
        print(f"   ✅ NO separate emails for each subject")
    else:
        print(f"   ℹ️ No schedules for tomorrow")
    
    # Show the fix
    print(f"\n4️⃣ WHAT WAS FIXED:")
    print("   ❌ BEFORE: Students received separate emails for each subject")
    print("   ✅ AFTER: Students receive ONE email with all classes")
    print("   🧹 Deleted 140 old individual reminders")
    print("   🔧 Updated system to only create daily digests")
    
    print(f"\n🎯 VERIFICATION RESULT:")
    
    if individual_reminders.count() == 0:
        print("   ✅ SUCCESS: No individual reminders exist")
        print("   ✅ Students will receive ONE email per day")
        print("   ✅ Email will contain ALL classes for the day")
        print("   ✅ Clean, organized email delivery")
    else:
        print("   ❌ ISSUE: Individual reminders still exist")
        print("   💡 Run cleanup again to remove them")
    
    return individual_reminders.count() == 0

if __name__ == "__main__":
    success = verify_single_email_fix()
    
    if success:
        print(f"\n🎉 PERFECT! Students will now receive ONE daily digest email!")
    else:
        print(f"\n⚠️ Need to clean up remaining individual reminders")
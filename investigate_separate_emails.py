#!/usr/bin/env python
"""
Investigate why students are receiving separate emails for each subject
"""

import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from reminders.models import Reminder
from accounts.models import User

def investigate_separate_emails():
    today = date.today()
    
    print("🔍 INVESTIGATING SEPARATE EMAIL ISSUE")
    print("=" * 60)
    print(f"📅 Date: {today}")
    
    # Check all reminders for today
    all_reminders = Reminder.objects.filter(digest_date=today)
    
    print(f"\n📧 ALL REMINDERS FOR TODAY:")
    print(f"   Total reminders: {all_reminders.count()}")
    
    # Group by student and type
    students = User.objects.filter(user_type='student')
    
    for student in students:
        student_reminders = all_reminders.filter(student=student)
        
        print(f"\n👤 {student.username}:")
        print(f"   Total reminders: {student_reminders.count()}")
        
        # Check by type
        daily_digests = student_reminders.filter(reminder_type='daily_digest')
        scheduled_reminders = student_reminders.filter(reminder_type='scheduled')
        other_reminders = student_reminders.exclude(reminder_type__in=['daily_digest', 'scheduled'])
        
        print(f"   📅 Daily digests: {daily_digests.count()}")
        print(f"   ⏰ Scheduled reminders: {scheduled_reminders.count()}")
        print(f"   📧 Other reminders: {other_reminders.count()}")
        
        # Show details
        for reminder in student_reminders:
            status = "✅ SENT" if reminder.is_sent else "⏳ PENDING"
            print(f"      • {reminder.reminder_type}: {status}")
            if reminder.schedule:
                print(f"        Subject: {reminder.schedule.subject_name}")
    
    print(f"\n🎯 DIAGNOSIS:")
    
    # Check if there are individual schedule reminders
    individual_reminders = Reminder.objects.filter(
        digest_date=today,
        reminder_type='scheduled',
        schedule__isnull=False
    )
    
    if individual_reminders.exists():
        print("   ❌ PROBLEM FOUND: Individual schedule reminders exist")
        print(f"   📧 {individual_reminders.count()} separate emails being sent")
        print("   💡 These should be combined into daily digests")
        
        print(f"\n   📋 INDIVIDUAL REMINDERS:")
        for reminder in individual_reminders:
            print(f"      • {reminder.student.username}: {reminder.schedule.subject_name}")
    
    # Check daily digests
    daily_digests = Reminder.objects.filter(
        digest_date=today,
        reminder_type='daily_digest'
    )
    
    if daily_digests.exists():
        print(f"\n   ✅ Daily digests exist: {daily_digests.count()}")
        print("   💡 These are the correct combined emails")
    else:
        print(f"\n   ❌ No daily digests found")
        print("   💡 Daily digests should be created instead of individual reminders")

if __name__ == "__main__":
    investigate_separate_emails()
#!/usr/bin/env python
"""
Clean up old individual reminders that cause separate emails
"""

import os
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from reminders.models import Reminder

def cleanup_old_reminders():
    print("🧹 CLEANING UP OLD INDIVIDUAL REMINDERS")
    print("=" * 60)
    
    # Find all individual schedule reminders (not daily digests)
    individual_reminders = Reminder.objects.filter(
        reminder_type='scheduled'
    )
    
    print(f"📧 Individual reminders found: {individual_reminders.count()}")
    
    if individual_reminders.exists():
        print("\n📋 INDIVIDUAL REMINDERS TO DELETE:")
        for reminder in individual_reminders[:10]:  # Show first 10
            schedule_name = reminder.schedule.subject_name if reminder.schedule else "No schedule"
            print(f"   • {reminder.student.username}: {schedule_name}")
        
        if individual_reminders.count() > 10:
            print(f"   ... and {individual_reminders.count() - 10} more")
        
        # Delete all individual reminders
        deleted_count = individual_reminders.count()
        individual_reminders.delete()
        
        print(f"\n✅ DELETED {deleted_count} individual reminders")
        print("💡 This prevents separate emails for each subject")
    else:
        print("✅ No individual reminders found")
    
    # Check for any other problematic reminders
    all_reminders = Reminder.objects.all()
    daily_digests = all_reminders.filter(reminder_type='daily_digest')
    other_reminders = all_reminders.exclude(reminder_type='daily_digest')
    
    print(f"\n📊 CURRENT REMINDER STATUS:")
    print(f"   📅 Daily digests: {daily_digests.count()} (GOOD)")
    print(f"   📧 Other reminders: {other_reminders.count()}")
    
    if other_reminders.exists():
        print(f"\n📋 OTHER REMINDERS:")
        for reminder in other_reminders:
            print(f"   • {reminder.reminder_type}: {reminder.student.username}")
    
    print(f"\n🎯 RESULT:")
    print("   ✅ Students will now receive ONE daily digest email")
    print("   ✅ No more separate emails for each subject")
    print("   ✅ Clean, organized email delivery")

if __name__ == "__main__":
    cleanup_old_reminders()
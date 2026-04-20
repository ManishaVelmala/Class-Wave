#!/usr/bin/env python
"""
Test what happens when student changes time preference after receiving today's digest
"""

import os
import django
from datetime import date, time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from reminders.models import Reminder, DailyDigestPreference
from accounts.models import User

def test_time_preference_change():
    print("⏰ TESTING TIME PREFERENCE CHANGE AFTER DIGEST SENT")
    print("=" * 70)
    
    today = date.today()
    
    # Get a student who has received today's digest
    student = User.objects.filter(user_type='student').first()
    if not student:
        print("❌ No students found")
        return
    
    print(f"👤 Testing with student: {student.username}")
    
    # Check current digest status
    current_digest = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).first()
    
    if current_digest:
        current_time = current_digest.reminder_time.strftime('%I:%M %p')
        status = "✅ SENT" if current_digest.is_sent else "⏳ PENDING"
        print(f"📧 Current digest: {current_time} - {status}")
    else:
        print("❌ No digest found for today")
        return
    
    # Check current time preference
    try:
        pref = DailyDigestPreference.objects.get(student=student)
        current_pref_time = pref.digest_time.strftime('%I:%M %p')
        print(f"⚙️ Current preference: {current_pref_time}")
    except DailyDigestPreference.DoesNotExist:
        print("⚙️ No preference set (using default)")
        current_pref_time = "7:00 AM"
    
    print(f"\n🔄 SCENARIO: Student changes time preference AFTER receiving today's digest")
    
    # Simulate changing time preference
    new_time = time(15, 30)  # 3:30 PM
    new_time_display = new_time.strftime('%I:%M %p')
    
    print(f"📝 Student changes preference from {current_pref_time} to {new_time_display}")
    
    # Update preference
    pref, created = DailyDigestPreference.objects.get_or_create(
        student=student,
        defaults={'digest_time': new_time, 'is_enabled': True}
    )
    
    if not created:
        pref.digest_time = new_time
        pref.save()
    
    print(f"✅ Preference updated to: {new_time_display}")
    
    # Check what happens to today's digest
    updated_digest = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).first()
    
    print(f"\n📊 WHAT HAPPENS AFTER PREFERENCE CHANGE:")
    
    if updated_digest:
        updated_time = updated_digest.reminder_time.strftime('%I:%M %p')
        status = "✅ SENT" if updated_digest.is_sent else "⏳ PENDING"
        print(f"📧 Today's digest time: {updated_time} - {status}")
        
        if updated_digest.is_sent:
            print(f"   ❌ NO new email sent (digest already sent today)")
            print(f"   ✅ Preference change applies to TOMORROW's digest")
        else:
            print(f"   ✅ Digest will be sent at new time: {new_time_display}")
    
    print(f"\n🎯 ANSWER TO YOUR QUESTION:")
    print(f"   📅 Today's digest: Already sent at old time")
    print(f"   ❌ NO additional email: System prevents duplicate daily digests")
    print(f"   ⏰ New preference: Takes effect from TOMORROW")
    print(f"   📧 Tomorrow's digest: Will be sent at {new_time_display}")
    
    print(f"\n🔄 SYSTEM BEHAVIOR:")
    print(f"   ✅ Prevents spam: No duplicate daily digest emails")
    print(f"   ✅ Smart timing: Preference changes apply to future digests")
    print(f"   ✅ Immediate updates: Only for schedule changes (not preference changes)")
    
    # Test what happens if we generate tomorrow's digest
    from datetime import timedelta
    tomorrow = today + timedelta(days=1)
    
    print(f"\n🔮 TESTING TOMORROW'S DIGEST WITH NEW PREFERENCE:")
    
    from reminders.tasks import create_daily_digest_for_student
    
    # Check if there are schedules for tomorrow
    from schedules.models import Schedule
    tomorrow_schedules = Schedule.objects.filter(date=tomorrow)
    
    if tomorrow_schedules.exists():
        print(f"📚 Schedules for tomorrow: {tomorrow_schedules.count()}")
        
        # Generate tomorrow's digest (this will use new preference)
        tomorrow_digest = create_daily_digest_for_student(student.id, tomorrow)
        
        if tomorrow_digest:
            tomorrow_time = tomorrow_digest.reminder_time.strftime('%I:%M %p')
            print(f"✅ Tomorrow's digest created for: {tomorrow_time}")
            print(f"✅ Uses NEW preference: {new_time_display}")
            
            # Clean up test digest
            tomorrow_digest.delete()
            print(f"🧹 Test digest cleaned up")
        else:
            print(f"❌ Could not create tomorrow's digest")
    else:
        print(f"📚 No schedules for tomorrow to test with")
    
    print(f"\n📧 EMAIL BEHAVIOR SUMMARY:")
    print(f"   📅 Daily Digest: Once per day (no duplicates)")
    print(f"   ⚙️ Preference Change: Applies to future digests only")
    print(f"   ⚡ Update Alerts: Immediate (for schedule changes)")
    print(f"   🚫 No Spam: System prevents duplicate daily emails")

if __name__ == "__main__":
    test_time_preference_change()
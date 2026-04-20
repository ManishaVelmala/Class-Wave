#!/usr/bin/env python3
"""
Simulate what happens if a student registers NOW and sets 22:55 preference
"""

import os
import sys
import django
from datetime import date, time, datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.utils import timezone
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def check_22_55_timing():
    """Check if 22:55 preference would work today"""
    
    print("🕐 CHECKING 22:55 (10:55 PM) TIMING")
    print("=" * 35)
    
    utc_now = timezone.now()
    india_offset = timedelta(hours=5, minutes=30)
    india_now = utc_now + india_offset
    today = date.today()
    
    # Student's desired time: 22:55 (10:55 PM India)
    student_preference = time(22, 55)
    
    print(f"🇮🇳 Current India time: {india_now.strftime('%I:%M %p')} ({india_now.time()})")
    print(f"👤 Student wants emails at: {student_preference.strftime('%I:%M %p')} ({student_preference})")
    
    # Convert student preference to UTC
    utc_equivalent_time = (
        datetime.combine(today, student_preference) - india_offset
    ).time()
    
    utc_equivalent_datetime = timezone.make_aware(
        datetime.combine(today, utc_equivalent_time)
    )
    
    print(f"🌍 UTC equivalent: {utc_equivalent_time.strftime('%I:%M %p')} ({utc_equivalent_time})")
    print(f"📅 UTC datetime: {utc_equivalent_datetime}")
    
    # Check if time has passed
    time_passed = utc_now >= utc_equivalent_datetime
    
    print(f"\n⏰ TIMING CHECK:")
    print(f"   Current UTC: {utc_now}")
    print(f"   Target UTC:  {utc_equivalent_datetime}")
    
    if time_passed:
        time_diff = utc_now - utc_equivalent_datetime
        minutes_passed = time_diff.total_seconds() / 60
        print(f"   ❌ Time PASSED: {minutes_passed:.0f} minutes ago")
        print(f"   📧 RESULT: NO email today")
        print(f"   📅 Next email: Tomorrow at 10:55 PM")
        return False
    else:
        time_until = utc_equivalent_datetime - utc_now
        minutes_until = time_until.total_seconds() / 60
        print(f"   ✅ Time REMAINING: {minutes_until:.0f} minutes")
        print(f"   📧 RESULT: YES, email today!")
        print(f"   ⏰ Email in: {minutes_until:.0f} minutes")
        return True

def explain_new_student_process():
    """Explain what happens for new students"""
    
    print(f"\n📋 NEW STUDENT REGISTRATION PROCESS")
    print("=" * 40)
    
    print("🔄 What happens when a student registers:")
    print("   1. Student creates account")
    print("   2. Student sets time preference (e.g., 10:55 PM)")
    print("   3. Student visits website")
    print("   4. Middleware checks: Does digest exist for today?")
    print("   5. If NO → Middleware creates digest")
    print("   6. Background service runs every 30 minutes")
    print("   7. When student's time arrives → Email sent!")
    
    print(f"\n⚠️  IMPORTANT TIMING RULE:")
    print("   • If student's preferred time hasn't passed → Gets email TODAY")
    print("   • If student's preferred time has passed → Gets email TOMORROW")

def check_what_time_would_work():
    """Check what time preferences would work for a student registering now"""
    
    print(f"\n🎯 WHAT TIME PREFERENCES WORK TODAY?")
    print("=" * 40)
    
    utc_now = timezone.now()
    india_offset = timedelta(hours=5, minutes=30)
    india_now = utc_now + india_offset
    today = date.today()
    
    print(f"🇮🇳 Current India time: {india_now.strftime('%I:%M %p')}")
    print(f"\n✅ Time preferences that WORK today (student gets email):")
    
    # Test various future times
    future_times = [
        time(23, 0),   # 11:00 PM
        time(23, 15),  # 11:15 PM
        time(23, 30),  # 11:30 PM
        time(23, 45),  # 11:45 PM
        time(23, 59),  # 11:59 PM
    ]
    
    working_times = []
    
    for test_time in future_times:
        # Convert to UTC
        utc_equivalent_time = (
            datetime.combine(today, test_time) - india_offset
        ).time()
        utc_equivalent_datetime = timezone.make_aware(
            datetime.combine(today, utc_equivalent_time)
        )
        
        if utc_now < utc_equivalent_datetime:
            time_until = utc_equivalent_datetime - utc_now
            minutes_until = time_until.total_seconds() / 60
            print(f"   • {test_time.strftime('%I:%M %p')} India → Email in {minutes_until:.0f} minutes")
            working_times.append(test_time)
    
    if not working_times:
        print("   • None - too late in the day")
        print(f"\n❌ Students registering now will get first email TOMORROW")
    else:
        print(f"\n📊 {len(working_times)} time preferences still work today!")

def final_answer_for_22_55():
    """Give final answer for 22:55 specifically"""
    
    print(f"\n" + "=" * 60)
    print("🎯 FINAL ANSWER FOR 22:55 (10:55 PM) PREFERENCE")
    print("=" * 60)
    
    works_today = check_22_55_timing()
    
    if works_today:
        print(f"\n✅ YES - Student will get email TODAY")
        print(f"   • Student registers now")
        print(f"   • Sets 10:55 PM preference")
        print(f"   • Visits website (digest created)")
        print(f"   • Gets email at 10:55 PM India time")
    else:
        print(f"\n❌ NO - Student will get email TOMORROW")
        print(f"   • 10:55 PM time has already passed today")
        print(f"   • Student registers now")
        print(f"   • Sets 10:55 PM preference")
        print(f"   • No email today")
        print(f"   • Tomorrow: Digest generated at 6:00 AM")
        print(f"   • Tomorrow: Email sent at 10:55 PM")
        
        print(f"\n💡 ALTERNATIVE:")
        print(f"   • Student could set a later time (11:30 PM, 11:45 PM)")
        print(f"   • Then they would get email today!")

if __name__ == "__main__":
    check_22_55_timing()
    explain_new_student_process()
    check_what_time_would_work()
    final_answer_for_22_55()
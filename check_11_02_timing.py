#!/usr/bin/env python3
"""
Check if 23:02 (11:02 PM) preference would get email today
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

def check_11_02_timing():
    """Check if 11:02 PM preference works today"""
    
    print("🕐 CHECKING 23:02 (11:02 PM) TIMING")
    print("=" * 35)
    
    utc_now = timezone.now()
    india_offset = timedelta(hours=5, minutes=30)
    india_now = utc_now + india_offset
    today = date.today()
    
    # Student's desired time: 23:02 (11:02 PM India)
    student_preference = time(23, 2)  # 11:02 PM
    
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
        return False
    else:
        time_until = utc_equivalent_datetime - utc_now
        minutes_until = time_until.total_seconds() / 60
        print(f"   ✅ Time REMAINING: {minutes_until:.0f} minutes")
        print(f"   📧 RESULT: YES, email today!")
        print(f"   ⏰ Email in: {minutes_until:.0f} minutes")
        return True

if __name__ == "__main__":
    works = check_11_02_timing()
    
    print(f"\n" + "=" * 50)
    print("🎯 ANSWER FOR 23:02 (11:02 PM)")
    print("=" * 50)
    
    if works:
        print("✅ YES - You WILL get the email today!")
        print("   • Time hasn't passed yet")
        print("   • System will send email at 11:02 PM India time")
        print("   • You just need to register and visit the website")
    else:
        print("❌ NO - Time has already passed")
        print("   • You'll get the email tomorrow")
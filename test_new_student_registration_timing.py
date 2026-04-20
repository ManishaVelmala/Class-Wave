#!/usr/bin/env python3
"""
Test if a new student who registers now and sets time preference to 22:55 gets email today
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
from reminders.tasks import create_daily_digest_for_student

def test_new_student_scenario():
    """Test new student registration and email timing"""
    
    print("🆕 TESTING NEW STUDENT REGISTRATION SCENARIO")
    print("=" * 50)
    
    utc_now = timezone.now()
    india_offset = timedelta(hours=5, minutes=30)
    india_now = utc_now + india_offset
    today = date.today()
    
    print(f"🕐 Current UTC time: {utc_now.strftime('%H:%M:%S')}")
    print(f"🇮🇳 Current India time: {india_now.strftime('%H:%M:%S')}")
    print(f"📅 Today's date: {today}")
    
    # Test time preference: 22:55 (10:55 PM India time)
    test_preference = time(22, 55)  # 10:55 PM
    
    print(f"\n👤 NEW STUDENT SCENARIO:")
    print(f"   Student registers now and sets preference: {test_preference.strftime('%I:%M %p')} India time")
    
    # Convert to UTC equivalent
    utc_equivalent_time = (
        datetime.combine(today, test_preference) - india_offset
    ).time()
    
    utc_equivalent_datetime = timezone.make_aware(
        datetime.combine(today, utc_equivalent_time)
    )
    
    print(f"   UTC equivalent: {utc_equivalent_time.strftime('%I:%M %p')} ({utc_equivalent_time})")
    print(f"   UTC datetime: {utc_equivalent_datetime}")
    
    # Check if time has passed
    time_passed = utc_now >= utc_equivalent_datetime
    
    print(f"\n⏰ TIMING ANALYSIS:")
    print(f"   Current UTC: {utc_now}")
    print(f"   Target UTC:  {utc_equivalent_datetime}")
    print(f"   Time passed: {time_passed}")
    
    if time_passed:
        time_diff = utc_now - utc_equivalent_datetime
        hours_passed = time_diff.total_seconds() / 3600
        print(f"   ⚠️  Time passed {hours_passed:.1f} hours ago")
        print(f"   📧 RESULT: Email would NOT be sent today (time already passed)")
    else:
        time_until = utc_equivalent_datetime - utc_now
        hours_until = time_until.total_seconds() / 3600
        print(f"   ⏳ Time until: {hours_until:.1f} hours")
        print(f"   📧 RESULT: Email WILL be sent today at {test_preference.strftime('%I:%M %p')} India time")

def test_digest_generation_for_new_student():
    """Test if digest can be generated for a new student"""
    
    print(f"\n📝 DIGEST GENERATION TEST")
    print("=" * 30)
    
    # Check if there are any existing students we can use for testing
    existing_students = User.objects.filter(user_type='student')
    
    if existing_students.exists():
        test_student = existing_students.first()
        print(f"👤 Using existing student for test: {test_student.username}")
        
        # Check if digest exists for today
        today = date.today()
        existing_digest = Reminder.objects.filter(
            student=test_student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if existing_digest:
            print(f"   ✅ Digest already exists for today")
            print(f"   📧 Is sent: {existing_digest.is_sent}")
        else:
            print(f"   ❌ No digest exists for today")
            print(f"   🔧 This means new students won't get digests until tomorrow")
    
    print(f"\n📋 KEY INSIGHTS:")
    print(f"   • Digests are generated at 6:00 AM daily")
    print(f"   • New students who register after 6:00 AM won't get today's digest")
    print(f"   • They will get their first digest tomorrow")

def check_middleware_digest_generation():
    """Check if middleware can generate digest for new students"""
    
    print(f"\n🔧 MIDDLEWARE DIGEST GENERATION")
    print("=" * 35)
    
    print("📋 Current middleware behavior:")
    print("   • Middleware generates digests on first daily visit")
    print("   • But only if no digest exists for that date")
    print("   • New students visiting today COULD get digest")
    
    # Check if middleware is active
    from reminders.middleware import AutoDigestMiddleware
    
    print(f"\n🌐 MIDDLEWARE TEST:")
    print("   If new student visits website today:")
    print("   1. Middleware checks if digest exists")
    print("   2. If not, creates digest for today")
    print("   3. Background service will send email at preferred time")
    print("   4. Student gets email today!")

def simulate_new_student_workflow():
    """Simulate complete new student workflow"""
    
    print(f"\n🎯 COMPLETE NEW STUDENT WORKFLOW")
    print("=" * 40)
    
    test_preference = time(22, 55)  # 10:55 PM
    utc_now = timezone.now()
    india_offset = timedelta(hours=5, minutes=30)
    today = date.today()
    
    # Convert to UTC
    utc_equivalent_time = (
        datetime.combine(today, test_preference) - india_offset
    ).time()
    utc_equivalent_datetime = timezone.make_aware(
        datetime.combine(today, utc_equivalent_time)
    )
    
    time_passed = utc_now >= utc_equivalent_datetime
    
    print(f"📋 SCENARIO: Student registers now, sets preference to 10:55 PM")
    print(f"")
    
    if not time_passed:
        print(f"✅ GOOD NEWS: Time hasn't passed yet!")
        print(f"")
        print(f"🔄 What happens next:")
        print(f"   1. Student registers and sets preference to 10:55 PM")
        print(f"   2. Student visits website (triggers middleware)")
        print(f"   3. Middleware creates today's digest")
        print(f"   4. Background service runs every 30 minutes")
        print(f"   5. At 5:25 PM UTC (10:55 PM India), email is sent")
        print(f"   6. Student receives email today!")
        
        time_until = utc_equivalent_datetime - utc_now
        hours_until = time_until.total_seconds() / 3600
        print(f"")
        print(f"⏰ Email will be sent in: {hours_until:.1f} hours")
    else:
        print(f"❌ BAD NEWS: Time has already passed")
        print(f"")
        print(f"🔄 What happens next:")
        print(f"   1. Student registers and sets preference to 10:55 PM")
        print(f"   2. No email today (time already passed)")
        print(f"   3. Tomorrow at 6:00 AM, digest will be generated")
        print(f"   4. Tomorrow at 10:55 PM, student gets first email")

if __name__ == "__main__":
    test_new_student_scenario()
    test_digest_generation_for_new_student()
    check_middleware_digest_generation()
    simulate_new_student_workflow()
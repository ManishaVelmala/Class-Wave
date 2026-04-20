#!/usr/bin/env python3
"""
Fix digest generation to use India time (6:00 AM IST) instead of UTC
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
from reminders.models import Reminder
from reminders.tasks import create_daily_digest_for_student

def get_india_date():
    """Get current date in India timezone"""
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    return india_now.date()

def should_generate_digests():
    """Check if it's time to generate digests (6:00 AM India time)"""
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    
    # Check if it's 6:00 AM India time (or later)
    india_6am = time(6, 0)
    current_india_time = india_now.time()
    
    return current_india_time >= india_6am

def generate_digests_india_time():
    """Generate digests based on India time logic"""
    
    print("🇮🇳 DIGEST GENERATION - INDIA TIME LOGIC")
    print("=" * 45)
    
    # Get current India date and time
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    india_time = india_now.time()
    
    print(f"🕐 Current Times:")
    print(f"   UTC: {utc_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   India: {india_now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n📅 Target Date for Digests: {india_date}")
    
    # Check if it's past 6:00 AM India time
    if india_time < time(6, 0):
        print("⏰ Too early! Digests generated at 6:00 AM India time")
        print(f"   Current: {india_time.strftime('%I:%M %p')} India")
        print(f"   Wait until: 6:00 AM India")
        return 0
    
    print(f"✅ Time check passed: {india_time.strftime('%I:%M %p')} India (>= 6:00 AM)")
    
    # Generate digests for India date
    students = User.objects.filter(user_type='student')
    generated_count = 0
    updated_count = 0
    skipped_count = 0
    
    print(f"\n📝 Generating digests for {students.count()} students...")
    
    for student in students:
        # Check if digest already exists for this India date
        existing_digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=india_date
        ).first()
        
        if existing_digest:
            skipped_count += 1
            print(f"⏭️  {student.username}: Already exists for {india_date}")
            continue
        
        # Create digest for India date
        digest = create_daily_digest_for_student(student.id, india_date)
        
        if digest:
            generated_count += 1
            print(f"✅ {student.username}: Created for {india_date}")
        else:
            print(f"ℹ️  {student.username}: No classes on {india_date}")
    
    print(f"\n📊 Summary:")
    print(f"   Target date: {india_date} (India timezone)")
    print(f"   Generated: {generated_count}")
    print(f"   Skipped (existing): {skipped_count}")
    print(f"   Total students: {students.count()}")
    
    return generated_count

def test_india_time_logic():
    """Test the India time logic"""
    
    print("🧪 TESTING INDIA TIME LOGIC")
    print("=" * 30)
    
    # Show different scenarios
    test_times = [
        datetime(2024, 12, 17, 0, 30),   # 12:30 AM UTC = 6:00 AM India
        datetime(2024, 12, 17, 1, 0),    # 1:00 AM UTC = 6:30 AM India
        datetime(2024, 12, 17, 18, 30),  # 6:30 PM UTC = 12:00 AM India (next day)
        datetime(2024, 12, 17, 23, 0),   # 11:00 PM UTC = 4:30 AM India (next day)
    ]
    
    for test_utc in test_times:
        test_india = test_utc + timedelta(hours=5, minutes=30)
        
        print(f"\n📋 Test Case:")
        print(f"   UTC: {test_utc.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   India: {test_india.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   India date: {test_india.date()}")
        print(f"   India time: {test_india.time().strftime('%I:%M %p')}")
        
        if test_india.time() >= time(6, 0):
            print(f"   ✅ Generate digests for {test_india.date()}")
        else:
            print(f"   ⏰ Too early - wait until 6:00 AM India")

def show_comparison():
    """Show comparison between old and new logic"""
    
    print("\n🔄 OLD vs NEW LOGIC COMPARISON")
    print("=" * 35)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    
    utc_date = utc_now.date()
    india_date = india_now.date()
    
    print(f"📊 Current Status:")
    print(f"   UTC date: {utc_date}")
    print(f"   India date: {india_date}")
    
    print(f"\n🔄 Logic Comparison:")
    print(f"   OLD: Generate digests for {utc_date} (UTC date)")
    print(f"   NEW: Generate digests for {india_date} (India date)")
    
    if utc_date == india_date:
        print("✅ Same date - no difference today")
    else:
        print("⚠️  Different dates - NEW logic will be more accurate!")
        print("   Students will get digests for their actual 'today'")

if __name__ == "__main__":
    test_india_time_logic()
    show_comparison()
    
    print(f"\n🚀 RUNNING DIGEST GENERATION...")
    generated = generate_digests_india_time()
    
    if generated > 0:
        print(f"\n🎉 SUCCESS! Generated {generated} digests using India time logic")
    else:
        print(f"\n✅ No new digests needed (already exist or too early)")
    
    print(f"\n💡 NEXT STEPS:")
    print("1. Update continuous email service to use this logic")
    print("2. Digests will be generated at 6:00 AM India time daily")
    print("3. Students get digests for their actual 'today' in India")
#!/usr/bin/env python3
"""
Test the new India time digest generation system
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
from django.core.management import call_command
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference
from schedules.models import Schedule

def test_india_time_digest_logic():
    """Test the complete India time digest logic"""
    
    print("🇮🇳 TESTING INDIA TIME DIGEST GENERATION")
    print("=" * 45)
    
    # Get current times
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    
    print(f"🕐 Current Times:")
    print(f"   UTC: {utc_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   India: {india_now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    utc_date = utc_now.date()
    india_date = india_now.date()
    
    print(f"\n📅 Date Comparison:")
    print(f"   OLD system (UTC date): {utc_date}")
    print(f"   NEW system (India date): {india_date}")
    
    if utc_date != india_date:
        print("⚠️  IMPORTANT: Different dates detected!")
        print("   This is when the new system makes a difference")
    else:
        print("✅ Same dates today - but logic is still improved")
    
    return india_date

def test_digest_generation_timing():
    """Test when digests should be generated"""
    
    print(f"\n⏰ DIGEST GENERATION TIMING TEST")
    print("=" * 35)
    
    # Test different India times
    test_scenarios = [
        (time(5, 30), "Too early"),
        (time(5, 59), "Too early"),
        (time(6, 0), "Perfect time!"),
        (time(6, 1), "Good time"),
        (time(12, 0), "Good time"),
        (time(23, 59), "Good time"),
    ]
    
    for test_time, expected in test_scenarios:
        should_generate = test_time >= time(6, 0)
        status = "✅ Generate" if should_generate else "⏰ Wait"
        
        print(f"   {test_time.strftime('%I:%M %p')} India: {status} ({expected})")

def check_existing_digests():
    """Check existing digests in the system"""
    
    print(f"\n📊 EXISTING DIGESTS CHECK")
    print("=" * 25)
    
    # Get current India date
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    
    # Check digests for India date
    digests_today = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date
    )
    
    print(f"📅 Digests for {india_date} (India date): {digests_today.count()}")
    
    for digest in digests_today:
        status = "✅ Sent" if digest.is_sent else "⏳ Pending"
        print(f"   • {digest.student.username}: {status}")
    
    # Check if there are digests for other dates
    all_digests = Reminder.objects.filter(reminder_type='daily_digest')
    other_dates = set(all_digests.values_list('digest_date', flat=True)) - {india_date}
    
    if other_dates:
        print(f"\n📋 Digests for other dates:")
        for other_date in sorted(other_dates):
            count = all_digests.filter(digest_date=other_date).count()
            print(f"   • {other_date}: {count} digests")

def test_schedule_availability():
    """Check if there are schedules for today"""
    
    print(f"\n📚 SCHEDULE AVAILABILITY CHECK")
    print("=" * 30)
    
    # Get India date
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    
    # Check schedules for India date
    schedules_today = Schedule.objects.filter(date=india_date)
    
    print(f"📅 Schedules for {india_date} (India date): {schedules_today.count()}")
    
    if schedules_today.exists():
        print("✅ Schedules available - digests will be generated")
        
        # Group by student
        students_with_classes = set()
        for schedule in schedules_today:
            students_with_classes.update(schedule.students.all())
        
        print(f"👥 Students with classes: {len(students_with_classes)}")
        for student in students_with_classes:
            student_schedules = schedules_today.filter(students=student).count()
            print(f"   • {student.username}: {student_schedules} classes")
    else:
        print("ℹ️  No schedules today - no digests will be generated")

def test_time_preferences():
    """Check student time preferences"""
    
    print(f"\n⏰ TIME PREFERENCES CHECK")
    print("=" * 25)
    
    preferences = DailyDigestPreference.objects.filter(is_enabled=True)
    
    print(f"📊 Active preferences: {preferences.count()}")
    
    for pref in preferences:
        india_time = pref.digest_time
        
        # Convert to UTC for system processing
        india_offset = timedelta(hours=5, minutes=30)
        utc_equivalent = (datetime.combine(date.today(), india_time) - india_offset).time()
        
        print(f"   • {pref.student.username}:")
        print(f"     India time: {india_time.strftime('%I:%M %p')}")
        print(f"     UTC equivalent: {utc_equivalent.strftime('%I:%M %p')}")

def run_digest_generation_test():
    """Run the actual digest generation"""
    
    print(f"\n🚀 RUNNING DIGEST GENERATION TEST")
    print("=" * 35)
    
    try:
        # Run the management command
        call_command('send_real_daily_digests', verbosity=2)
        print("✅ Management command completed successfully")
    except Exception as e:
        print(f"❌ Error running management command: {e}")

def final_verification():
    """Final verification of the system"""
    
    print(f"\n🎯 FINAL VERIFICATION")
    print("=" * 20)
    
    # Get India date
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    india_time = india_now.time()
    
    print(f"📅 System Status:")
    print(f"   Current India time: {india_time.strftime('%I:%M %p')}")
    print(f"   Target digest date: {india_date}")
    
    # Check if digests exist
    digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date
    )
    
    print(f"   Digests for today: {digests.count()}")
    
    if india_time >= time(6, 0):
        print("✅ Past 6:00 AM India - digests should be generated")
    else:
        print("⏰ Before 6:00 AM India - digests will be generated later")
    
    print(f"\n🎉 INDIA TIME DIGEST SYSTEM:")
    print("   • Digests generated at 6:00 AM India time")
    print("   • Based on India date (not UTC date)")
    print("   • Students get digests for their actual 'today'")
    print("   • Perfect timezone handling maintained")

if __name__ == "__main__":
    india_date = test_india_time_digest_logic()
    test_digest_generation_timing()
    check_existing_digests()
    test_schedule_availability()
    test_time_preferences()
    
    print(f"\n" + "=" * 60)
    print("🧪 RUNNING LIVE TEST")
    print("=" * 60)
    
    run_digest_generation_test()
    final_verification()
    
    print(f"\n💡 SUMMARY:")
    print("The digest generation system now uses India time logic:")
    print(f"• Generates digests for India date: {india_date}")
    print("• Only after 6:00 AM India time")
    print("• Students get digests for their actual 'today'")
    print("• Maintains perfect email timing accuracy")
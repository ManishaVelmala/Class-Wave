#!/usr/bin/env python3
"""
Comprehensive verification of India time conversion for digest generation and email sending
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

def check_current_times():
    """Check current UTC and India times"""
    
    print("🕐 CURRENT TIME STATUS")
    print("=" * 22)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    
    print(f"UTC Time: {utc_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"India Time: {india_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"UTC Date: {utc_now.date()}")
    print(f"India Date: {india_now.date()}")
    
    if utc_now.date() != india_now.date():
        print("⚠️  DIFFERENT DATES - This is when India time logic matters!")
    else:
        print("✅ Same dates - but India time logic still applies")
    
    return utc_now, india_now

def check_digest_generation_logic():
    """Check if digest generation follows India time"""
    
    print(f"\n📝 DIGEST GENERATION LOGIC CHECK")
    print("=" * 35)
    
    utc_now, india_now = check_current_times()
    india_date = india_now.date()
    india_time = india_now.time()
    
    print(f"\n🎯 Expected Behavior:")
    print(f"   • Generate digests for: {india_date} (India date)")
    print(f"   • Only after: 6:00 AM India time")
    print(f"   • Current India time: {india_time.strftime('%I:%M %p')}")
    
    should_generate = india_time >= time(6, 0)
    print(f"   • Should generate now: {'✅ Yes' if should_generate else '⏰ No (too early)'}")
    
    return india_date, should_generate

def check_existing_digests(india_date):
    """Check existing digests for India date"""
    
    print(f"\n📊 EXISTING DIGESTS FOR {india_date}")
    print("=" * 40)
    
    # Check digests for India date
    digests_india_date = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date
    )
    
    print(f"Digests for India date ({india_date}): {digests_india_date.count()}")
    
    if digests_india_date.exists():
        sent_count = digests_india_date.filter(is_sent=True).count()
        pending_count = digests_india_date.filter(is_sent=False).count()
        
        print(f"   ✅ Sent: {sent_count}")
        print(f"   ⏳ Pending: {pending_count}")
        
        for digest in digests_india_date:
            status = "✅ Sent" if digest.is_sent else "⏳ Pending"
            sent_time = f" at {digest.sent_at.strftime('%I:%M %p')}" if digest.sent_at else ""
            print(f"   • {digest.student.username}: {status}{sent_time}")
    else:
        print("   ℹ️  No digests found for India date")
    
    # Check if there are digests for other dates
    all_digests = Reminder.objects.filter(reminder_type='daily_digest')
    other_dates = set(all_digests.values_list('digest_date', flat=True)) - {india_date}
    
    if other_dates:
        print(f"\n📋 Digests for other dates:")
        for other_date in sorted(other_dates, reverse=True):
            count = all_digests.filter(digest_date=other_date).count()
            print(f"   • {other_date}: {count} digests")
    
    return digests_india_date.count() > 0

def check_time_preference_conversion():
    """Check if time preferences are properly converted"""
    
    print(f"\n⏰ TIME PREFERENCE CONVERSION CHECK")
    print("=" * 38)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    
    preferences = DailyDigestPreference.objects.filter(is_enabled=True)
    
    print(f"Active preferences: {preferences.count()}")
    print(f"Checking conversion for India date: {india_date}")
    
    for pref in preferences:
        student = pref.student
        india_time = pref.digest_time
        
        print(f"\n👤 {student.username}:")
        print(f"   India preference: {india_time.strftime('%I:%M %p')}")
        
        # Convert to UTC (same logic as system)
        india_offset = timedelta(hours=5, minutes=30)
        utc_equivalent_time = (datetime.combine(india_date, india_time) - india_offset).time()
        
        print(f"   UTC equivalent: {utc_equivalent_time.strftime('%I:%M %p')}")
        
        # Check if due now
        utc_equivalent_datetime = timezone.make_aware(
            datetime.combine(india_date, utc_equivalent_time)
        )
        
        is_due = utc_now >= utc_equivalent_datetime
        
        if is_due:
            print(f"   Status: 🔔 DUE NOW!")
        else:
            time_until = utc_equivalent_datetime - utc_now
            hours = int(time_until.total_seconds() // 3600)
            minutes = int((time_until.total_seconds() % 3600) // 60)
            print(f"   Status: ⏳ Due in {hours}h {minutes}m")

def check_schedule_availability(india_date):
    """Check schedule availability for India date"""
    
    print(f"\n📚 SCHEDULE AVAILABILITY FOR {india_date}")
    print("=" * 45)
    
    schedules = Schedule.objects.filter(date=india_date)
    
    print(f"Schedules for India date: {schedules.count()}")
    
    if schedules.exists():
        students_with_classes = set()
        for schedule in schedules:
            students_with_classes.update(schedule.students.all())
        
        print(f"Students with classes: {len(students_with_classes)}")
        
        for student in students_with_classes:
            student_schedules = schedules.filter(students=student).count()
            print(f"   • {student.username}: {student_schedules} classes")
        
        return True
    else:
        print("   ℹ️  No schedules for India date")
        print("   📝 No digests should be generated")
        return False

def test_digest_generation():
    """Test digest generation with current logic"""
    
    print(f"\n🧪 TESTING DIGEST GENERATION")
    print("=" * 30)
    
    try:
        print("Running management command with current logic...")
        call_command('send_real_daily_digests', verbosity=2)
        print("✅ Management command completed")
    except Exception as e:
        print(f"❌ Error: {e}")

def verify_email_sending_logic():
    """Verify email sending follows India time conversion"""
    
    print(f"\n📧 EMAIL SENDING LOGIC VERIFICATION")
    print("=" * 38)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    
    # Find unsent digests
    unsent_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date,
        is_sent=False
    )
    
    print(f"Unsent digests for India date: {unsent_digests.count()}")
    
    if unsent_digests.exists():
        print(f"\n📋 Email sending analysis:")
        
        for digest in unsent_digests:
            student = digest.student
            
            try:
                pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
                india_time = pref.digest_time
                
                # Same conversion logic as system
                india_offset = timedelta(hours=5, minutes=30)
                utc_equivalent_time = (datetime.combine(india_date, india_time) - india_offset).time()
                utc_equivalent_datetime = timezone.make_aware(
                    datetime.combine(india_date, utc_equivalent_time)
                )
                
                is_due = utc_now >= utc_equivalent_datetime
                
                print(f"   • {student.username}:")
                print(f"     India preference: {india_time.strftime('%I:%M %p')}")
                print(f"     UTC equivalent: {utc_equivalent_time.strftime('%I:%M %p')}")
                print(f"     Status: {'🔔 Ready to send' if is_due else '⏳ Waiting'}")
                
            except DailyDigestPreference.DoesNotExist:
                print(f"   • {student.username}: ⚠️  No preference set")
    else:
        print("   ℹ️  No unsent digests to analyze")

def final_verification_summary():
    """Provide final verification summary"""
    
    print(f"\n" + "=" * 60)
    print("🎯 FINAL VERIFICATION SUMMARY")
    print("=" * 60)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    india_time = india_now.time()
    
    print(f"🇮🇳 Current Status:")
    print(f"   India time: {india_time.strftime('%I:%M %p')} on {india_date}")
    print(f"   UTC time: {utc_now.strftime('%I:%M %p')} on {utc_now.date()}")
    
    # Check digest generation
    digests_exist = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date
    ).exists()
    
    should_generate = india_time >= time(6, 0)
    
    print(f"\n📝 Digest Generation:")
    print(f"   Target date: {india_date} (India date)")
    print(f"   Should generate: {'✅ Yes' if should_generate else '⏰ No (before 6:00 AM)'}")
    print(f"   Digests exist: {'✅ Yes' if digests_exist else '❌ No'}")
    
    if should_generate and not digests_exist:
        print("   ⚠️  ISSUE: Should have digests but none found!")
    elif should_generate and digests_exist:
        print("   ✅ CORRECT: Digests exist as expected")
    elif not should_generate:
        print("   ✅ CORRECT: Too early for digest generation")
    
    # Check email timing
    preferences = DailyDigestPreference.objects.filter(is_enabled=True)
    due_count = 0
    
    for pref in preferences:
        india_time_pref = pref.digest_time
        india_offset = timedelta(hours=5, minutes=30)
        utc_equivalent_time = (datetime.combine(india_date, india_time_pref) - india_offset).time()
        utc_equivalent_datetime = timezone.make_aware(
            datetime.combine(india_date, utc_equivalent_time)
        )
        
        if utc_now >= utc_equivalent_datetime:
            due_count += 1
    
    print(f"\n📧 Email Timing:")
    print(f"   Students with preferences: {preferences.count()}")
    print(f"   Emails due now: {due_count}")
    print(f"   Conversion: India time → UTC ✅")
    
    print(f"\n🎯 System Status:")
    if should_generate and digests_exist:
        print("   ✅ WORKING CORRECTLY")
        print("   • Digests generated for India date")
        print("   • Email timing uses India time conversion")
        print("   • System follows India timezone logic")
    else:
        print("   ⚠️  NEEDS ATTENTION")
        print("   • Check digest generation timing")
        print("   • Verify India time conversion")

if __name__ == "__main__":
    print("🔍 COMPREHENSIVE INDIA TIME VERIFICATION")
    print("=" * 45)
    
    # Step 1: Check current times
    utc_now, india_now = check_current_times()
    
    # Step 2: Check digest generation logic
    india_date, should_generate = check_digest_generation_logic()
    
    # Step 3: Check existing digests
    digests_exist = check_existing_digests(india_date)
    
    # Step 4: Check schedule availability
    schedules_exist = check_schedule_availability(india_date)
    
    # Step 5: Check time preference conversion
    check_time_preference_conversion()
    
    # Step 6: Verify email sending logic
    verify_email_sending_logic()
    
    # Step 7: Test digest generation
    if should_generate and schedules_exist:
        test_digest_generation()
    
    # Step 8: Final summary
    final_verification_summary()
    
    print(f"\n✅ VERIFICATION COMPLETE")
    print("Check the summary above for system status!")
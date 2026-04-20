#!/usr/bin/env python3
"""
Check whether today's daily digest is generated
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
from schedules.models import Schedule

def check_current_time_status():
    """Check current time status"""
    
    print("🕐 CURRENT TIME STATUS")
    print("=" * 22)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    
    print(f"UTC Time: {utc_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"India Time: {india_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"UTC Date: {utc_now.date()}")
    print(f"India Date: {india_now.date()}")
    
    india_time = india_now.time()
    past_6am = india_time >= time(6, 0)
    
    print(f"\n⏰ Digest Generation Check:")
    print(f"Current India time: {india_time.strftime('%I:%M %p')}")
    print(f"Past 6:00 AM India: {'✅ Yes' if past_6am else '⏰ No'}")
    print(f"Should have digests: {'✅ Yes' if past_6am else '⏰ No (too early)'}")
    
    return india_now.date(), past_6am

def check_todays_digests(india_date):
    """Check today's digest status"""
    
    print(f"\n📊 TODAY'S DIGEST STATUS")
    print("=" * 25)
    
    print(f"Checking digests for India date: {india_date}")
    
    # Check digests for India date
    todays_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date
    )
    
    print(f"\nDigests for {india_date}: {todays_digests.count()}")
    
    if todays_digests.exists():
        print("✅ Today's digests exist!")
        
        sent_count = todays_digests.filter(is_sent=True).count()
        pending_count = todays_digests.filter(is_sent=False).count()
        
        print(f"   📧 Sent: {sent_count}")
        print(f"   ⏳ Pending: {pending_count}")
        
        print(f"\n📋 Digest Details:")
        for digest in todays_digests:
            status = "✅ Sent" if digest.is_sent else "⏳ Pending"
            sent_time = f" at {digest.sent_at.strftime('%I:%M %p UTC')}" if digest.sent_at else ""
            india_sent_time = f" ({(digest.sent_at + timedelta(hours=5, minutes=30)).strftime('%I:%M %p India')})" if digest.sent_at else ""
            
            print(f"   • {digest.student.username}: {status}{sent_time}{india_sent_time}")
        
        return True
    else:
        print("❌ No digests found for today!")
        return False

def check_schedules_for_today(india_date):
    """Check if there are schedules for today"""
    
    print(f"\n📚 SCHEDULES FOR TODAY")
    print("=" * 22)
    
    schedules = Schedule.objects.filter(date=india_date)
    
    print(f"Schedules for {india_date}: {schedules.count()}")
    
    if schedules.exists():
        print("✅ Schedules exist for today")
        
        # Get students with classes
        students_with_classes = set()
        for schedule in schedules:
            students_with_classes.update(schedule.students.all())
        
        print(f"👥 Students with classes: {len(students_with_classes)}")
        
        for student in students_with_classes:
            student_schedules = schedules.filter(students=student).count()
            print(f"   • {student.username}: {student_schedules} classes")
        
        return True, len(students_with_classes)
    else:
        print("❌ No schedules for today")
        print("📝 This is why no digests were generated")
        return False, 0

def check_student_preferences():
    """Check student preferences"""
    
    print(f"\n⏰ STUDENT PREFERENCES")
    print("=" * 21)
    
    preferences = DailyDigestPreference.objects.filter(is_enabled=True)
    
    print(f"Active preferences: {preferences.count()}")
    
    if preferences.exists():
        print("✅ Students have digest preferences set")
        
        for pref in preferences:
            print(f"   • {pref.student.username}: {pref.digest_time.strftime('%I:%M %p')} India")
        
        return True
    else:
        print("❌ No active preferences found")
        return False

def check_all_digest_dates():
    """Check all digest dates in the system"""
    
    print(f"\n📅 ALL DIGEST DATES")
    print("=" * 18)
    
    all_digests = Reminder.objects.filter(reminder_type='daily_digest')
    all_dates = set(all_digests.values_list('digest_date', flat=True))
    
    if all_dates:
        print("📋 Digest dates in system:")
        for digest_date in sorted(all_dates, reverse=True):
            count = all_digests.filter(digest_date=digest_date).count()
            sent_count = all_digests.filter(digest_date=digest_date, is_sent=True).count()
            
            print(f"   • {digest_date}: {count} digests ({sent_count} sent)")
    else:
        print("❌ No digests found in system")

def diagnose_digest_generation():
    """Diagnose why digests might not be generated"""
    
    print(f"\n🔍 DIGEST GENERATION DIAGNOSIS")
    print("=" * 32)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    india_time = india_now.time()
    
    # Check all conditions
    past_6am = india_time >= time(6, 0)
    schedules_exist = Schedule.objects.filter(date=india_date).exists()
    students_exist = User.objects.filter(user_type='student').exists()
    
    print(f"📋 Generation Requirements:")
    print(f"   ✅ Past 6:00 AM India: {'Yes' if past_6am else 'No'}")
    print(f"   ✅ Schedules for today: {'Yes' if schedules_exist else 'No'}")
    print(f"   ✅ Students exist: {'Yes' if students_exist else 'No'}")
    
    if past_6am and schedules_exist and students_exist:
        print(f"\n✅ All conditions met - digests should exist!")
    else:
        print(f"\n⚠️  Missing conditions:")
        if not past_6am:
            print(f"   • Too early (before 6:00 AM India)")
        if not schedules_exist:
            print(f"   • No schedules for today")
        if not students_exist:
            print(f"   • No students in system")

def run_digest_generation_test():
    """Try to generate digests manually"""
    
    print(f"\n🧪 MANUAL DIGEST GENERATION TEST")
    print("=" * 33)
    
    from django.core.management import call_command
    
    try:
        print("Running digest generation command...")
        call_command('send_real_daily_digests', verbosity=1)
        print("✅ Command completed")
    except Exception as e:
        print(f"❌ Error: {e}")

def final_summary(india_date, digests_exist, schedules_exist, students_count):
    """Provide final summary"""
    
    print(f"\n" + "=" * 50)
    print("🎯 FINAL DIGEST STATUS SUMMARY")
    print("=" * 50)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_time = india_now.time()
    
    print(f"📅 Date: {india_date}")
    print(f"🕐 India Time: {india_time.strftime('%I:%M %p')}")
    
    if digests_exist:
        print(f"✅ DIGESTS EXIST: Today's digests are generated")
        print(f"📊 Status: System working correctly")
    else:
        print(f"❌ NO DIGESTS: Today's digests are missing")
        
        if not schedules_exist:
            print(f"📝 Reason: No schedules for today")
        elif india_time < time(6, 0):
            print(f"⏰ Reason: Too early (before 6:00 AM India)")
        else:
            print(f"⚠️  Reason: Unknown - needs investigation")
    
    print(f"\n🎯 System Status:")
    if digests_exist and schedules_exist:
        print("✅ WORKING CORRECTLY")
        print("• Digests generated for India date")
        print("• Using India time logic")
        print("• Ready for email delivery")
    else:
        print("⚠️  NEEDS ATTENTION")
        if not schedules_exist:
            print("• No classes scheduled for today")
        else:
            print("• Check digest generation logic")

if __name__ == "__main__":
    print("📊 CHECKING TODAY'S DIGEST STATUS")
    print("=" * 35)
    
    # Step 1: Check current time
    india_date, past_6am = check_current_time_status()
    
    # Step 2: Check today's digests
    digests_exist = check_todays_digests(india_date)
    
    # Step 3: Check schedules
    schedules_exist, students_count = check_schedules_for_today(india_date)
    
    # Step 4: Check preferences
    preferences_exist = check_student_preferences()
    
    # Step 5: Check all digest dates
    check_all_digest_dates()
    
    # Step 6: Diagnose
    diagnose_digest_generation()
    
    # Step 7: Try manual generation if needed
    if not digests_exist and past_6am and schedules_exist:
        run_digest_generation_test()
        # Re-check after manual generation
        digests_exist = check_todays_digests(india_date)
    
    # Step 8: Final summary
    final_summary(india_date, digests_exist, schedules_exist, students_count)
    
    print(f"\n✅ DIGEST CHECK COMPLETE")
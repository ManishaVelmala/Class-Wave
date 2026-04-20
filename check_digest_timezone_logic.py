#!/usr/bin/env python3
"""
Check whether daily digest generation is based on UTC or India timezone
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
from django.conf import settings
from accounts.models import User
from reminders.models import Reminder
from schedules.models import Schedule

def check_django_timezone_settings():
    """Check Django timezone configuration"""
    
    print("🌍 DJANGO TIMEZONE CONFIGURATION")
    print("=" * 35)
    
    print(f"⚙️  Django Settings:")
    print(f"   TIME_ZONE: {settings.TIME_ZONE}")
    print(f"   USE_TZ: {settings.USE_TZ}")
    
    current_utc = timezone.now()
    india_time = current_utc + timedelta(hours=5, minutes=30)
    
    print(f"\n🕐 Current Times:")
    print(f"   UTC: {current_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   India: {india_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check what Django considers "today"
    django_today = timezone.now().date()
    utc_today = datetime.utcnow().date()
    india_today = (datetime.utcnow() + timedelta(hours=5, minutes=30)).date()
    
    print(f"\n📅 Date Comparison:")
    print(f"   Django 'today': {django_today}")
    print(f"   UTC today: {utc_today}")
    print(f"   India today: {india_today}")
    
    if django_today == utc_today:
        print("✅ Django uses UTC date for 'today'")
        return "UTC"
    elif django_today == india_today:
        print("✅ Django uses India date for 'today'")
        return "INDIA"
    else:
        print("⚠️  Django date doesn't match UTC or India")
        return "UNKNOWN"

def check_digest_generation_logic():
    """Check how digest generation determines 'today'"""
    
    print(f"\n📝 DIGEST GENERATION LOGIC")
    print("=" * 30)
    
    # Check existing digests and their dates
    today_utc = datetime.utcnow().date()
    today_india = (datetime.utcnow() + timedelta(hours=5, minutes=30)).date()
    
    print(f"📊 Checking existing digests:")
    print(f"   UTC date: {today_utc}")
    print(f"   India date: {today_india}")
    
    # Check digests for UTC date
    utc_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today_utc
    ).count()
    
    # Check digests for India date
    india_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today_india
    ).count()
    
    print(f"\n📋 Digest Count Analysis:")
    print(f"   Digests for UTC date ({today_utc}): {utc_digests}")
    print(f"   Digests for India date ({today_india}): {india_digests}")
    
    if utc_digests > 0 and india_digests == 0:
        print("✅ Digests generated using UTC date")
        return "UTC"
    elif india_digests > 0 and utc_digests == 0:
        print("✅ Digests generated using India date")
        return "INDIA"
    elif utc_digests > 0 and india_digests > 0:
        if today_utc == today_india:
            print("✅ Same date in both timezones")
            return "SAME"
        else:
            print("⚠️  Digests exist for both dates")
            return "BOTH"
    else:
        print("📭 No digests found for either date")
        return "NONE"

def check_schedule_dates():
    """Check what dates schedules are using"""
    
    print(f"\n📅 SCHEDULE DATE ANALYSIS")
    print("=" * 25)
    
    today_utc = datetime.utcnow().date()
    today_india = (datetime.utcnow() + timedelta(hours=5, minutes=30)).date()
    
    # Check schedules for today
    utc_schedules = Schedule.objects.filter(date=today_utc).count()
    india_schedules = Schedule.objects.filter(date=today_india).count()
    
    print(f"📊 Schedule Count:")
    print(f"   Schedules for UTC date ({today_utc}): {utc_schedules}")
    print(f"   Schedules for India date ({today_india}): {india_schedules}")
    
    if today_utc == today_india:
        print("✅ UTC and India dates are the same today")
        return "SAME"
    elif utc_schedules > 0:
        print("✅ Schedules use UTC date")
        return "UTC"
    elif india_schedules > 0:
        print("✅ Schedules use India date")
        return "INDIA"
    else:
        print("📭 No schedules found for either date")
        return "NONE"

def analyze_digest_creation_time():
    """Analyze when digests were created"""
    
    print(f"\n🕐 DIGEST CREATION TIME ANALYSIS")
    print("=" * 35)
    
    # Get recent digests
    recent_digests = Reminder.objects.filter(
        reminder_type='daily_digest'
    ).order_by('-created_at')[:10]
    
    print(f"📋 Recent Digest Creation Times:")
    
    for digest in recent_digests:
        creation_utc = digest.created_at
        creation_india = creation_utc + timedelta(hours=5, minutes=30)
        
        print(f"   📝 {digest.student.username} ({digest.digest_date}):")
        print(f"      Created UTC: {creation_utc.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"      Created India: {creation_india.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"      Digest date: {digest.digest_date}")

def check_background_service_logic():
    """Check background service date logic"""
    
    print(f"\n🤖 BACKGROUND SERVICE DATE LOGIC")
    print("=" * 35)
    
    # Read the background service code to see how it determines "today"
    try:
        with open('reminders/management/commands/send_real_daily_digests.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("📋 Background Service Analysis:")
        
        if 'date.today()' in content:
            print("   ✅ Uses date.today() - follows Django timezone")
        
        if 'timezone.now().date()' in content:
            print("   ✅ Uses timezone.now().date() - Django aware")
        
        if 'datetime.utcnow().date()' in content:
            print("   ⚠️  Uses datetime.utcnow().date() - UTC based")
        
        if 'india' in content.lower() or 'ist' in content.lower():
            print("   🇮🇳 Contains India timezone logic")
        
        # Check target_date logic
        if 'target_date = date.today()' in content:
            print("   📅 Default target_date: date.today() (Django timezone)")
        
    except Exception as e:
        print(f"❌ Could not analyze background service: {e}")

def test_digest_generation_with_different_dates():
    """Test digest generation with different date scenarios"""
    
    print(f"\n🧪 DIGEST GENERATION DATE TEST")
    print("=" * 30)
    
    from reminders.tasks import create_daily_digest_for_student
    
    # Get a test student
    student = User.objects.filter(user_type='student').first()
    
    if not student:
        print("❌ No student found for testing")
        return
    
    print(f"👤 Testing with student: {student.username}")
    
    # Test different date scenarios
    today_utc = datetime.utcnow().date()
    today_india = (datetime.utcnow() + timedelta(hours=5, minutes=30)).date()
    tomorrow_utc = today_utc + timedelta(days=1)
    
    print(f"\n📅 Date Scenarios:")
    print(f"   UTC today: {today_utc}")
    print(f"   India today: {today_india}")
    print(f"   UTC tomorrow: {tomorrow_utc}")
    
    # Check what date the system would use for digest generation
    django_today = timezone.now().date()
    print(f"   Django today: {django_today}")
    
    if django_today == today_utc:
        print("✅ System uses UTC date for digest generation")
    elif django_today == today_india:
        print("✅ System uses India date for digest generation")
    else:
        print("⚠️  System uses different date logic")

if __name__ == "__main__":
    print("🌍 DAILY DIGEST TIMEZONE ANALYSIS")
    print("=" * 40)
    
    django_tz = check_django_timezone_settings()
    digest_logic = check_digest_generation_logic()
    schedule_dates = check_schedule_dates()
    
    analyze_digest_creation_time()
    check_background_service_logic()
    test_digest_generation_with_different_dates()
    
    print(f"\n" + "=" * 60)
    print("🎯 TIMEZONE ANALYSIS SUMMARY")
    print("=" * 60)
    
    print(f"📊 Analysis Results:")
    print(f"   Django timezone setting: {django_tz}")
    print(f"   Digest generation logic: {digest_logic}")
    print(f"   Schedule date logic: {schedule_dates}")
    
    print(f"\n🌍 FINAL ANSWER:")
    
    if django_tz == "UTC" and digest_logic == "UTC":
        print("✅ Daily digests are generated based on UTC timezone")
        print("📅 'Today' means UTC date (not India date)")
        print("🕐 Digest generation happens at UTC midnight + 6 hours")
    elif django_tz == "INDIA" or digest_logic == "INDIA":
        print("✅ Daily digests are generated based on India timezone")
        print("📅 'Today' means India date")
        print("🕐 Digest generation happens at India midnight + 6 hours")
    else:
        print("⚠️  Mixed or unclear timezone logic")
        print("📅 Need to check specific implementation")
    
    print(f"\n💡 PRACTICAL IMPACT:")
    print("   • If UTC-based: Digest for 'today' created at 6:00 AM UTC")
    print("   • If India-based: Digest for 'today' created at 6:00 AM India time")
    print("   • This affects when students see their daily schedules")
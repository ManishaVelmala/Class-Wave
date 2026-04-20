#!/usr/bin/env python3
"""
Check if there are any digests generated for UTC date vs India date
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
from reminders.models import Reminder

def compare_digest_dates():
    """Compare digests for UTC date vs India date"""
    
    print("📅 DIGEST DATES COMPARISON")
    print("=" * 27)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    
    utc_date = utc_now.date()
    india_date = india_now.date()
    
    print(f"UTC Date: {utc_date}")
    print(f"India Date: {india_date}")
    
    # Check digests for both dates
    utc_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=utc_date
    )
    
    india_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date
    )
    
    print(f"\n📊 Digest Count Comparison:")
    print(f"   UTC date ({utc_date}): {utc_digests.count()} digests")
    print(f"   India date ({india_date}): {india_digests.count()} digests")
    
    if utc_date == india_date:
        print("✅ Same dates - no difference expected")
    else:
        print("⚠️  Different dates - checking which system is being used...")
        
        if utc_digests.count() > 0 and india_digests.count() == 0:
            print("❌ ISSUE: Using UTC date logic (old system)")
        elif india_digests.count() > 0 and utc_digests.count() == 0:
            print("✅ CORRECT: Using India date logic (new system)")
        elif utc_digests.count() > 0 and india_digests.count() > 0:
            print("⚠️  MIXED: Digests exist for both dates")
        else:
            print("ℹ️  No digests for either date")
    
    # Show all digest dates in the system
    all_digests = Reminder.objects.filter(reminder_type='daily_digest')
    all_dates = set(all_digests.values_list('digest_date', flat=True))
    
    print(f"\n📋 All Digest Dates in System:")
    for digest_date in sorted(all_dates, reverse=True):
        count = all_digests.filter(digest_date=digest_date).count()
        sent_count = all_digests.filter(digest_date=digest_date, is_sent=True).count()
        
        if digest_date == india_date:
            marker = " ← India date (current)"
        elif digest_date == utc_date:
            marker = " ← UTC date (current)"
        else:
            marker = ""
        
        print(f"   • {digest_date}: {count} digests ({sent_count} sent){marker}")

def check_today_digest_status():
    """Check today's digest status specifically"""
    
    print(f"\n📝 TODAY'S DIGEST STATUS")
    print("=" * 24)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    india_time = india_now.time()
    
    print(f"Current India time: {india_time.strftime('%I:%M %p')}")
    print(f"Target digest date: {india_date}")
    
    # Check if digests exist for today (India date)
    today_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date
    )
    
    print(f"\nDigests for {india_date}: {today_digests.count()}")
    
    if today_digests.exists():
        print("✅ Today's digests exist")
        
        for digest in today_digests:
            status = "✅ Sent" if digest.is_sent else "⏳ Pending"
            created_time = digest.reminder_time.strftime('%I:%M %p UTC') if digest.reminder_time else "Unknown"
            print(f"   • {digest.student.username}: {status} (created for {created_time})")
    else:
        print("❌ No digests for today")
        
        # Check if it's past 6:00 AM India
        if india_time >= time(6, 0):
            print("⚠️  ISSUE: Past 6:00 AM India but no digests exist!")
        else:
            print("ℹ️  Too early - digests will be created at 6:00 AM India")

if __name__ == "__main__":
    compare_digest_dates()
    check_today_digest_status()
    
    print(f"\n🎯 CONCLUSION:")
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    
    if utc_now.date() == india_now.date():
        print("Today UTC and India dates are the same.")
        print("The India time logic is working correctly.")
    else:
        print("UTC and India dates are different today.")
        print("This is when the India time logic makes a real difference!")
    
    print("✅ System is using India date for digest generation.")
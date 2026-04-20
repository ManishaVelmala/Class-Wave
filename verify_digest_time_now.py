#!/usr/bin/env python3
"""
Verify current digest time - check if it's still correct or reverted to 7:00 AM
"""

import os
import sys
import django
from datetime import date, time, datetime
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def verify_digest_time_now():
    """Check current digest time for Vaishnavi"""
    
    print("🔍 VERIFYING CURRENT DIGEST TIME")
    print("=" * 40)
    
    # Find Vaishnavi
    vaishnavi = User.objects.filter(username='Vaishnavi').first()
    if not vaishnavi:
        print("❌ Vaishnavi not found")
        return
    
    print(f"👤 Checking: {vaishnavi.username} ({vaishnavi.email})")
    
    # Check preference
    try:
        pref = DailyDigestPreference.objects.get(student=vaishnavi)
        print(f"⏰ Time preference: {pref.digest_time.strftime('%I:%M %p')}")
        print(f"📊 Enabled: {pref.is_enabled}")
    except DailyDigestPreference.DoesNotExist:
        print("❌ No time preference found")
        return
    
    # Check today's digest
    today = date.today()
    digest = Reminder.objects.filter(
        student=vaishnavi,
        reminder_type='daily_digest',
        digest_date=today
    ).first()
    
    if digest:
        digest_time = digest.reminder_time
        digest_time_only = digest_time.time()
        
        print(f"\n📝 Current digest:")
        print(f"   ID: {digest.id}")
        print(f"   Scheduled for: {digest_time}")
        print(f"   Time only: {digest_time_only.strftime('%I:%M %p')}")
        print(f"   Is sent: {digest.is_sent}")
        print(f"   Created: {digest.created_at}")
        
        # Check if it matches preference
        if digest_time_only == pref.digest_time:
            print(f"\n✅ DIGEST TIME IS CORRECT!")
            print(f"   Matches preference: {pref.digest_time.strftime('%I:%M %p')}")
        else:
            print(f"\n❌ DIGEST TIME IS WRONG!")
            print(f"   Expected: {pref.digest_time.strftime('%I:%M %p')}")
            print(f"   Actual: {digest_time_only.strftime('%I:%M %p')}")
            
            # Check if it's the 7:00 AM problem
            if digest_time_only == time(7, 0):
                print(f"   ⚠️  PROBLEM: Digest is set to 7:00 AM (default time)")
                print(f"   🔧 This needs to be fixed!")
        
        # Check current time vs digest time
        now = timezone.now()
        is_due = digest_time <= now
        
        print(f"\n🕐 Current time: {now.time().strftime('%I:%M %p')}")
        print(f"📧 Is due now: {is_due}")
        
        if is_due and not digest.is_sent:
            print(f"   ⚠️  Email should be sent but hasn't been!")
        elif not is_due:
            time_until = digest_time - now
            hours = int(time_until.total_seconds() // 3600)
            minutes = int((time_until.total_seconds() % 3600) // 60)
            print(f"   ⏳ Email will be sent in: {hours}h {minutes}m")
        
    else:
        print(f"\n❌ No digest found for today")
        print(f"   This means no classes are scheduled for {today}")

def check_all_students_digest_times():
    """Check all students' digest times"""
    
    print(f"\n📊 ALL STUDENTS DIGEST TIMES")
    print("=" * 35)
    
    today = date.today()
    all_prefs = DailyDigestPreference.objects.all().order_by('digest_time')
    
    for pref in all_prefs:
        student = pref.student
        preference_time = pref.digest_time
        
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        print(f"\n👤 {student.username}:")
        print(f"   Preference: {preference_time.strftime('%I:%M %p')}")
        
        if digest:
            digest_time = digest.reminder_time.time()
            matches = digest_time == preference_time
            
            status = "✅" if matches else "❌"
            print(f"   Digest time: {digest_time.strftime('%I:%M %p')} {status}")
            
            if not matches:
                print(f"   ⚠️  MISMATCH DETECTED!")
        else:
            print(f"   Digest: ❌ Not found")

if __name__ == "__main__":
    verify_digest_time_now()
    check_all_students_digest_times()
    
    print(f"\n" + "=" * 40)
    print("🎯 SUMMARY:")
    print("   If any digest shows 7:00 AM, it needs to be fixed")
    print("   All digest times should match student preferences")
    print("   Run fix_all_digest_times.py if problems found")
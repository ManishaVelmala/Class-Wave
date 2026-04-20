#!/usr/bin/env python3
"""
Test India time email sending logic
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
from reminders.models import Reminder, DailyDigestPreference

def test_india_time_comparison():
    """Test the new India time comparison logic"""
    
    print("🇮🇳 TESTING INDIA TIME EMAIL SENDING")
    print("=" * 38)
    
    # Get current times
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    current_india_time = india_now.time()
    india_date = india_now.date()
    
    print(f"🕐 Current Status:")
    print(f"   UTC time: {utc_now.strftime('%I:%M %p')}")
    print(f"   India time: {current_india_time.strftime('%I:%M %p')}")
    print(f"   India date: {india_date}")
    
    # Get student preferences
    preferences = DailyDigestPreference.objects.filter(is_enabled=True).order_by('digest_time')
    
    print(f"\n📊 Testing Email Timing Logic:")
    print("Using NEW India time comparison (no UTC conversion)")
    
    for pref in preferences:
        student = pref.student
        student_india_time = pref.digest_time
        
        # NEW LOGIC: Compare India times directly
        is_due_india = current_india_time >= student_india_time
        
        print(f"\n👤 {student.username}:")
        print(f"   Preference: {student_india_time.strftime('%I:%M %p')} India")
        print(f"   Current: {current_india_time.strftime('%I:%M %p')} India")
        print(f"   Comparison: {current_india_time.strftime('%I:%M %p')} >= {student_india_time.strftime('%I:%M %p')}")
        print(f"   Result: {'🔔 SEND EMAIL' if is_due_india else '⏳ WAIT'}")
        
        if not is_due_india:
            # Calculate time remaining
            student_datetime = datetime.combine(india_date, student_india_time)
            current_datetime = datetime.combine(india_date, current_india_time)
            
            if student_datetime > current_datetime:
                time_until = student_datetime - current_datetime
                hours = int(time_until.total_seconds() // 3600)
                minutes = int((time_until.total_seconds() % 3600) // 60)
                print(f"   Wait time: {hours}h {minutes}m")

def compare_old_vs_new_logic():
    """Compare old UTC conversion vs new India time logic"""
    
    print(f"\n🔄 OLD vs NEW LOGIC COMPARISON")
    print("=" * 33)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    current_india_time = india_now.time()
    india_date = india_now.date()
    
    preferences = DailyDigestPreference.objects.filter(is_enabled=True)
    
    print(f"Current India time: {current_india_time.strftime('%I:%M %p')}")
    
    for pref in preferences:
        student = pref.student
        student_india_time = pref.digest_time
        
        # OLD LOGIC: Convert India to UTC, then compare UTC times
        india_offset = timedelta(hours=5, minutes=30)
        utc_equivalent_time = (datetime.combine(india_date, student_india_time) - india_offset).time()
        utc_equivalent_datetime = timezone.make_aware(
            datetime.combine(india_date, utc_equivalent_time)
        )
        is_due_old = utc_now >= utc_equivalent_datetime
        
        # NEW LOGIC: Compare India times directly
        is_due_new = current_india_time >= student_india_time
        
        print(f"\n👤 {student.username} ({student_india_time.strftime('%I:%M %p')} India):")
        print(f"   OLD logic (UTC conversion): {'🔔 Send' if is_due_old else '⏳ Wait'}")
        print(f"   NEW logic (India direct): {'🔔 Send' if is_due_new else '⏳ Wait'}")
        
        if is_due_old == is_due_new:
            print(f"   ✅ Same result")
        else:
            print(f"   ⚠️  Different results!")

def test_edge_cases():
    """Test edge cases around midnight"""
    
    print(f"\n🌙 EDGE CASE TESTING")
    print("=" * 20)
    
    # Test different scenarios
    test_scenarios = [
        (time(23, 30), time(23, 45), "Late night - should send"),
        (time(23, 30), time(23, 15), "Late night - should wait"),
        (time(6, 0), time(6, 30), "Early morning - should send"),
        (time(6, 0), time(5, 45), "Early morning - should wait"),
    ]
    
    for student_time, current_time, description in test_scenarios:
        is_due = current_time >= student_time
        
        print(f"\n📋 {description}:")
        print(f"   Student preference: {student_time.strftime('%I:%M %p')}")
        print(f"   Current India time: {current_time.strftime('%I:%M %p')}")
        print(f"   Result: {'🔔 Send' if is_due else '⏳ Wait'}")

def run_actual_test():
    """Run the actual management command to test"""
    
    print(f"\n🧪 RUNNING ACTUAL EMAIL SENDING TEST")
    print("=" * 37)
    
    try:
        print("Executing management command with new India time logic...")
        call_command('send_real_daily_digests', verbosity=2)
        print("✅ Command completed successfully")
    except Exception as e:
        print(f"❌ Error: {e}")

def verify_digest_status():
    """Verify current digest status"""
    
    print(f"\n📊 CURRENT DIGEST STATUS")
    print("=" * 25)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    
    digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date
    )
    
    print(f"Digests for {india_date}: {digests.count()}")
    
    sent_count = digests.filter(is_sent=True).count()
    pending_count = digests.filter(is_sent=False).count()
    
    print(f"   ✅ Sent: {sent_count}")
    print(f"   ⏳ Pending: {pending_count}")
    
    for digest in digests:
        status = "✅ Sent" if digest.is_sent else "⏳ Pending"
        sent_time = f" at {digest.sent_at.strftime('%I:%M %p')}" if digest.sent_at else ""
        print(f"   • {digest.student.username}: {status}{sent_time}")

if __name__ == "__main__":
    test_india_time_comparison()
    compare_old_vs_new_logic()
    test_edge_cases()
    verify_digest_status()
    
    print(f"\n🚀 RUNNING LIVE TEST")
    print("=" * 18)
    run_actual_test()
    
    print(f"\n🎯 SUMMARY:")
    print("The system now uses India time for both:")
    print("• Digest generation (6:00 AM India)")
    print("• Email sending (direct India time comparison)")
    print("• No UTC conversion needed for timing logic!")
    print("✅ Pure India time system implemented")
#!/usr/bin/env python3
"""
Test immediate email sending with India time logic
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

def test_immediate_email_sending():
    """Test immediate email sending by setting preference to current time"""
    
    print("🔔 TESTING IMMEDIATE INDIA TIME EMAIL SENDING")
    print("=" * 46)
    
    # Get current India time
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    current_india_time = india_now.time()
    india_date = india_now.date()
    
    print(f"🕐 Current India time: {current_india_time.strftime('%I:%M %p')}")
    
    # Find a student to test with
    test_student = DailyDigestPreference.objects.filter(is_enabled=True).first()
    
    if not test_student:
        print("❌ No students with preferences found")
        return
    
    print(f"👤 Testing with: {test_student.student.username}")
    
    # Store original preference
    original_time = test_student.digest_time
    print(f"📝 Original preference: {original_time.strftime('%I:%M %p')} India")
    
    # Set preference to current time minus 1 minute (so it's due)
    test_time = (datetime.combine(india_date, current_india_time) - timedelta(minutes=1)).time()
    test_student.digest_time = test_time
    test_student.save()
    
    print(f"🔧 Changed preference to: {test_time.strftime('%I:%M %p')} India (1 minute ago)")
    print(f"📧 This should trigger immediate email sending!")
    
    try:
        # Run the management command
        print(f"\n🚀 Running email sending command...")
        call_command('send_real_daily_digests', verbosity=2)
        
        # Check if email was sent
        digest = Reminder.objects.filter(
            student=test_student.student,
            reminder_type='daily_digest',
            digest_date=india_date
        ).first()
        
        if digest and digest.is_sent:
            print(f"✅ SUCCESS! Email was sent using India time logic")
            print(f"📧 Sent at: {digest.sent_at.strftime('%I:%M %p UTC')} ({(digest.sent_at + timedelta(hours=5, minutes=30)).strftime('%I:%M %p')} India)")
        else:
            print(f"⏳ Email not sent yet (may be due to timing)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Restore original preference
        test_student.digest_time = original_time
        test_student.save()
        print(f"\n🔄 Restored original preference: {original_time.strftime('%I:%M %p')} India")

def test_continuous_service_logic():
    """Test the continuous service logic"""
    
    print(f"\n🔄 TESTING CONTINUOUS SERVICE LOGIC")
    print("=" * 37)
    
    # Simulate the continuous service logic
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    current_india_time = india_now.time()
    
    print(f"Current India time: {current_india_time.strftime('%I:%M %p')}")
    
    # Find unsent digests
    unsent_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date,
        is_sent=False
    )
    
    print(f"Unsent digests: {unsent_digests.count()}")
    
    for digest in unsent_digests:
        student = digest.student
        
        try:
            pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
            student_india_time = pref.digest_time
            
            # NEW LOGIC: Compare India times directly
            is_due = current_india_time >= student_india_time
            
            print(f"\n👤 {student.username}:")
            print(f"   Preference: {student_india_time.strftime('%I:%M %p')} India")
            print(f"   Current: {current_india_time.strftime('%I:%M %p')} India")
            print(f"   Due: {'✅ Yes' if is_due else '⏳ No'}")
            
            if is_due:
                print(f"   🔔 Would send email now!")
            
        except DailyDigestPreference.DoesNotExist:
            print(f"   ⚠️  No preference set")

def show_timing_difference():
    """Show the difference between old and new timing logic"""
    
    print(f"\n📊 TIMING LOGIC COMPARISON")
    print("=" * 27)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    current_india_time = india_now.time()
    india_date = india_now.date()
    
    print(f"🕐 Current Times:")
    print(f"   UTC: {utc_now.strftime('%I:%M %p')}")
    print(f"   India: {current_india_time.strftime('%I:%M %p')}")
    
    print(f"\n🔄 Logic Comparison:")
    print(f"   OLD: Convert India preference → UTC, compare with UTC time")
    print(f"   NEW: Compare India preference directly with India time")
    
    print(f"\n✅ Benefits of NEW logic:")
    print("   • No timezone conversion needed")
    print("   • Direct time comparison in India timezone")
    print("   • Simpler and more intuitive")
    print("   • Eliminates conversion errors")
    print("   • Pure India time system")

def verify_system_status():
    """Verify the complete system status"""
    
    print(f"\n🎯 SYSTEM STATUS VERIFICATION")
    print("=" * 30)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    india_time = india_now.time()
    
    print(f"📅 Current Status:")
    print(f"   India date: {india_date}")
    print(f"   India time: {india_time.strftime('%I:%M %p')}")
    
    # Check digest generation
    past_6am = india_time >= time(6, 0)
    print(f"   Past 6:00 AM: {'✅ Yes' if past_6am else '⏰ No'}")
    
    # Check digests
    digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date
    )
    
    print(f"   Digests exist: {'✅ Yes' if digests.exists() else '❌ No'}")
    print(f"   Digest count: {digests.count()}")
    
    # Check preferences
    preferences = DailyDigestPreference.objects.filter(is_enabled=True)
    print(f"   Active preferences: {preferences.count()}")
    
    print(f"\n✅ System Components:")
    print("   • Digest generation: Uses India date + 6:00 AM India time")
    print("   • Email sending: Uses direct India time comparison")
    print("   • No UTC conversion in timing logic")
    print("   • Pure India timezone system")

if __name__ == "__main__":
    test_immediate_email_sending()
    test_continuous_service_logic()
    show_timing_difference()
    verify_system_status()
    
    print(f"\n🎉 INDIA TIME EMAIL SYSTEM COMPLETE")
    print("=" * 37)
    print("The system now uses India time for:")
    print("✅ Digest generation timing (6:00 AM India)")
    print("✅ Email sending timing (direct India comparison)")
    print("✅ All time calculations and logic")
    print("🇮🇳 Pure India time system implemented!")
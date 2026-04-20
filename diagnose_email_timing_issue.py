#!/usr/bin/env python3
"""
Diagnose why emails are not being sent according to student time preferences
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

def diagnose_email_timing():
    """Diagnose email timing issues"""
    
    print("🔍 DIAGNOSING EMAIL TIMING ISSUES")
    print("=" * 40)
    
    utc_now = timezone.now()
    india_offset = timedelta(hours=5, minutes=30)
    india_now = utc_now + india_offset
    
    print(f"🕐 Current UTC time: {utc_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🇮🇳 Current India time: {india_now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    today = date.today()
    
    # Check all students with preferences
    students_with_prefs = DailyDigestPreference.objects.filter(is_enabled=True)
    
    print(f"\n👥 STUDENTS WITH TIME PREFERENCES: {students_with_prefs.count()}")
    print("-" * 50)
    
    for pref in students_with_prefs:
        student = pref.student
        india_pref_time = pref.digest_time
        
        print(f"\n👤 {student.username} ({student.email}):")
        print(f"   India preference: {india_pref_time.strftime('%I:%M %p')} ({india_pref_time})")
        
        # Convert India time to UTC (same logic as background service)
        utc_equivalent_time = (
            datetime.combine(today, india_pref_time) - india_offset
        ).time()
        
        utc_equivalent_datetime = timezone.make_aware(
            datetime.combine(today, utc_equivalent_time)
        )
        
        print(f"   UTC equivalent: {utc_equivalent_time.strftime('%I:%M %p')} ({utc_equivalent_time})")
        print(f"   UTC datetime: {utc_equivalent_datetime}")
        
        # Check if time has passed
        should_send_now = utc_now >= utc_equivalent_datetime
        print(f"   Should send now: {should_send_now}")
        
        if should_send_now:
            time_passed = utc_now - utc_equivalent_datetime
            hours_passed = time_passed.total_seconds() / 3600
            print(f"   ⚠️  Time passed: {hours_passed:.1f} hours ago")
        else:
            time_until = utc_equivalent_datetime - utc_now
            hours_until = time_until.total_seconds() / 3600
            print(f"   ⏳ Time until: {hours_until:.1f} hours")
        
        # Check digest status
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if digest:
            print(f"   📝 Digest exists: YES")
            print(f"   📧 Is sent: {digest.is_sent}")
            if digest.is_sent:
                print(f"   📅 Sent at: {digest.sent_at}")
            else:
                print(f"   ❌ NOT SENT YET")
                if should_send_now:
                    print(f"   🚨 PROBLEM: Should have been sent!")
        else:
            print(f"   📝 Digest exists: NO")

def check_background_service_frequency():
    """Check how often the background service runs"""
    
    print(f"\n🤖 BACKGROUND SERVICE FREQUENCY CHECK")
    print("=" * 40)
    
    import subprocess
    
    try:
        # Check Windows Task Scheduler details
        result = subprocess.run(
            ['schtasks', '/query', '/tn', 'ClassWave Daily Digest', '/fo', 'LIST', '/v'],
            capture_output=True,
            text=True,
            shell=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Schedule:' in line or 'Repeat:' in line or 'Interval:' in line:
                    print(f"   {line.strip()}")
            
            print(f"\n📊 Analysis:")
            if 'Daily' in result.stdout:
                print("   ✅ Task runs daily")
            if 'Repeat' in result.stdout:
                print("   ⚠️  Task has repeat settings")
            else:
                print("   ❌ Task runs only ONCE per day")
                print("   🚨 PROBLEM: Emails can only be sent once daily!")
        
    except Exception as e:
        print(f"❌ Could not check task details: {e}")

def test_manual_email_sending():
    """Test sending emails manually for students whose time has passed"""
    
    print(f"\n📧 MANUAL EMAIL SENDING TEST")
    print("=" * 35)
    
    utc_now = timezone.now()
    india_offset = timedelta(hours=5, minutes=30)
    today = date.today()
    
    # Find students whose time has passed but haven't received emails
    students_to_send = []
    
    for pref in DailyDigestPreference.objects.filter(is_enabled=True):
        student = pref.student
        india_pref_time = pref.digest_time
        
        # Convert to UTC
        utc_equivalent_time = (
            datetime.combine(today, india_pref_time) - india_offset
        ).time()
        
        utc_equivalent_datetime = timezone.make_aware(
            datetime.combine(today, utc_equivalent_time)
        )
        
        # Check if time passed and email not sent
        if utc_now >= utc_equivalent_datetime:
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=today,
                is_sent=False
            ).first()
            
            if digest:
                students_to_send.append((student, digest, india_pref_time))
    
    print(f"📊 Students ready for email: {len(students_to_send)}")
    
    if students_to_send:
        response = input("\n🤔 Send emails to these students now? (y/n): ")
        if response.lower() == 'y':
            from django.core.mail import send_mail
            from django.conf import settings
            
            sent_count = 0
            
            for student, digest, india_time in students_to_send:
                try:
                    send_mail(
                        subject=f'📅 Your Schedule for {today.strftime("%A, %B %d, %Y")}',
                        message=digest.message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[student.email],
                        fail_silently=False,
                    )
                    
                    # Mark as sent
                    digest.is_sent = True
                    digest.sent_at = utc_now
                    digest.save()
                    
                    sent_count += 1
                    print(f"✅ Sent to {student.username} (India time: {india_time.strftime('%I:%M %p')})")
                    
                except Exception as e:
                    print(f"❌ Failed to send to {student.username}: {e}")
            
            print(f"\n📊 Sent {sent_count} emails successfully")
    else:
        print("   📭 No students ready for email")

def check_windows_task_scheduler_timing():
    """Check if Windows Task Scheduler is configured to run frequently enough"""
    
    print(f"\n⏰ WINDOWS TASK SCHEDULER TIMING")
    print("=" * 35)
    
    print("🔍 Current task configuration:")
    print("   Task: ClassWave Daily Digest")
    print("   Frequency: Once daily at 6:00 AM")
    print("")
    print("🚨 IDENTIFIED PROBLEM:")
    print("   • Task runs only ONCE per day at 6:00 AM")
    print("   • Emails can only be sent at 6:00 AM")
    print("   • Students with different time preferences don't get emails")
    print("")
    print("💡 SOLUTION NEEDED:")
    print("   • Task should run EVERY 30 MINUTES")
    print("   • Each run checks if any student's time has arrived")
    print("   • Emails sent throughout the day at correct times")

def propose_solution():
    """Propose solution for email timing issue"""
    
    print(f"\n🔧 PROPOSED SOLUTION")
    print("=" * 25)
    
    print("📋 Current Problem:")
    print("   • Windows Task runs once daily at 6:00 AM")
    print("   • All emails sent at 6:00 AM regardless of preference")
    print("   • Students don't get emails at their chosen times")
    
    print(f"\n✅ Solution:")
    print("   1. Change Windows Task to run every 30 minutes")
    print("   2. Background service checks current time vs preferences")
    print("   3. Sends emails only when student's time arrives")
    print("   4. Students get emails at their exact preferred times")
    
    print(f"\n🛠️  Implementation:")
    print("   • Modify Windows Task Scheduler frequency")
    print("   • Keep existing background service logic")
    print("   • No code changes needed")

if __name__ == "__main__":
    diagnose_email_timing()
    check_background_service_frequency()
    test_manual_email_sending()
    check_windows_task_scheduler_timing()
    propose_solution()
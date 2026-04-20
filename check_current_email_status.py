#!/usr/bin/env python3
"""
Check current email status for the user who set 23:03 preference
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

def check_current_email_status():
    """Check why email wasn't sent for 23:03 preference"""
    
    print("🔍 CHECKING CURRENT EMAIL STATUS")
    print("=" * 35)
    
    utc_now = timezone.now()
    india_offset = timedelta(hours=5, minutes=30)
    india_now = utc_now + india_offset
    today = date.today()
    
    print(f"🕐 Current UTC time: {utc_now.strftime('%H:%M:%S')}")
    print(f"🇮🇳 Current India time: {india_now.strftime('%H:%M:%S')}")
    
    # Find user with 23:03 preference
    pref_23_03 = DailyDigestPreference.objects.filter(
        digest_time=time(23, 3),
        is_enabled=True
    ).first()
    
    if pref_23_03:
        student = pref_23_03.student
        print(f"\n👤 Found student with 23:03 preference:")
        print(f"   Username: {student.username}")
        print(f"   Email: {student.email}")
        print(f"   Preference: {pref_23_03.digest_time}")
        
        # Check if digest exists
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if digest:
            print(f"\n📝 Digest Status:")
            print(f"   Digest exists: YES")
            print(f"   Created at: {digest.created_at}")
            print(f"   Scheduled time: {digest.reminder_time}")
            print(f"   Is sent: {digest.is_sent}")
            if digest.is_sent:
                print(f"   Sent at: {digest.sent_at}")
            
            # Check timing
            utc_equivalent_time = (
                datetime.combine(today, pref_23_03.digest_time) - india_offset
            ).time()
            
            utc_equivalent_datetime = timezone.make_aware(
                datetime.combine(today, utc_equivalent_time)
            )
            
            print(f"\n⏰ Timing Analysis:")
            print(f"   India preference: {pref_23_03.digest_time} (23:03)")
            print(f"   UTC equivalent: {utc_equivalent_time}")
            print(f"   UTC target time: {utc_equivalent_datetime}")
            print(f"   Current UTC: {utc_now}")
            
            time_passed = utc_now >= utc_equivalent_datetime
            print(f"   Time passed: {time_passed}")
            
            if time_passed:
                time_diff = utc_now - utc_equivalent_datetime
                minutes_passed = time_diff.total_seconds() / 60
                print(f"   Time since target: {minutes_passed:.1f} minutes")
                
                if not digest.is_sent:
                    print(f"\n🚨 PROBLEM IDENTIFIED:")
                    print(f"   • Time has passed ({minutes_passed:.1f} minutes ago)")
                    print(f"   • But email was NOT sent")
                    print(f"   • This indicates a system issue")
                else:
                    print(f"\n✅ Email was sent {minutes_passed:.1f} minutes ago")
            else:
                time_until = utc_equivalent_datetime - utc_now
                minutes_until = time_until.total_seconds() / 60
                print(f"   Time until target: {minutes_until:.1f} minutes")
        else:
            print(f"\n❌ No digest found for today")
            print(f"   This means no digest was created")
            print(f"   Student needs to visit website to create digest")
    else:
        print(f"\n❌ No student found with 23:03 preference")
        
        # Check all current preferences
        all_prefs = DailyDigestPreference.objects.filter(is_enabled=True)
        print(f"\n📋 All current preferences:")
        for pref in all_prefs:
            print(f"   • {pref.student.username}: {pref.digest_time}")

def check_background_service_status():
    """Check if background service is running"""
    
    print(f"\n🤖 BACKGROUND SERVICE STATUS")
    print("=" * 30)
    
    import subprocess
    
    try:
        result = subprocess.run(
            ['schtasks', '/query', '/tn', 'ClassWave Daily Digest'],
            capture_output=True,
            text=True,
            shell=True
        )
        
        if result.returncode == 0:
            print("✅ Windows Task Scheduler: Running")
            
            # Check last run time
            if "Last Run Time:" in result.stdout:
                for line in result.stdout.split('\n'):
                    if "Last Run Time:" in line:
                        print(f"   {line.strip()}")
            
            if "Next Run Time:" in result.stdout:
                for line in result.stdout.split('\n'):
                    if "Next Run Time:" in line:
                        print(f"   {line.strip()}")
        else:
            print("❌ Windows Task Scheduler: Not found")
            
    except Exception as e:
        print(f"⚠️  Could not check scheduler: {e}")

def manual_email_test():
    """Test sending email manually"""
    
    print(f"\n📧 MANUAL EMAIL TEST")
    print("=" * 20)
    
    # Find the student with 23:03 preference
    pref_23_03 = DailyDigestPreference.objects.filter(
        digest_time=time(23, 3),
        is_enabled=True
    ).first()
    
    if pref_23_03:
        student = pref_23_03.student
        today = date.today()
        
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if digest and not digest.is_sent:
            response = input(f"🤔 Send email to {student.username} now? (y/n): ")
            if response.lower() == 'y':
                from django.core.mail import send_mail
                from django.conf import settings
                
                try:
                    send_mail(
                        subject=f'📅 Your Schedule for {today.strftime("%A, %B %d, %Y")}',
                        message=digest.message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[student.email],
                        fail_silently=False,
                    )
                    
                    digest.is_sent = True
                    digest.sent_at = timezone.now()
                    digest.save()
                    
                    print(f"✅ Email sent successfully to {student.email}")
                    
                except Exception as e:
                    print(f"❌ Failed to send email: {e}")
            else:
                print("❌ Email test cancelled")
        else:
            print("⚠️  No unsent digest found")
    else:
        print("❌ No student with 23:03 preference found")

if __name__ == "__main__":
    check_current_email_status()
    check_background_service_status()
    manual_email_test()
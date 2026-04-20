#!/usr/bin/env python3
"""
Complete fix for timezone and automation issues
"""

import os
import sys
import django
from datetime import date, time, datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference
from django.conf import settings

def fix_timezone_in_settings():
    """Fix Django timezone setting for India"""
    
    print("🔧 FIXING TIMEZONE SETTINGS")
    print("=" * 35)
    
    # Check current timezone setting
    current_tz = settings.TIME_ZONE
    print(f"📊 Current Django TIME_ZONE: {current_tz}")
    
    if current_tz != 'Asia/Kolkata':
        print("⚠️  Django is not set to India timezone!")
        print("🔧 Need to change TIME_ZONE = 'Asia/Kolkata' in settings.py")
        
        # Read current settings
        try:
            with open('lecturebuzz/settings.py', 'r') as f:
                content = f.read()
            
            # Check if TIME_ZONE is set
            if 'TIME_ZONE' in content:
                print("✅ TIME_ZONE setting found in settings.py")
                
                # Show what needs to be changed
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'TIME_ZONE' in line and not line.strip().startswith('#'):
                        print(f"   Current line {i+1}: {line.strip()}")
                        print(f"   Should be: TIME_ZONE = 'Asia/Kolkata'")
                        break
            else:
                print("❌ TIME_ZONE setting not found in settings.py")
                
        except Exception as e:
            print(f"❌ Error reading settings.py: {e}")
    else:
        print("✅ Django timezone is correctly set to Asia/Kolkata")

def check_current_digest_with_new_time():
    """Check current digest with new 10:10 PM preference"""
    
    print(f"\n👤 CHECKING NEW 10:10 PM PREFERENCE")
    print("=" * 40)
    
    # Find student with 10:10 PM preference
    target_time = time(22, 10)  # 10:10 PM
    pref = DailyDigestPreference.objects.filter(
        digest_time=target_time,
        is_enabled=True
    ).first()
    
    if not pref:
        print("❌ No student with 10:10 PM preference found")
        return
    
    student = pref.student
    print(f"👤 Student: {student.username}")
    print(f"⏰ Preference: {pref.digest_time.strftime('%I:%M %p')}")
    
    # Check current digest
    today = date.today()
    digest = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).first()
    
    if digest:
        print(f"📝 Current digest:")
        print(f"   Scheduled for: {digest.reminder_time}")
        print(f"   Is sent: {digest.is_sent}")
        
        # Check if digest time matches preference
        digest_time = digest.reminder_time.time()
        if digest_time != target_time:
            print(f"   ⚠️  DIGEST TIME MISMATCH!")
            print(f"   Expected: {target_time.strftime('%I:%M %p')}")
            print(f"   Actual: {digest_time.strftime('%I:%M %p')}")
            
            # Fix the digest time
            correct_datetime = datetime.combine(today, target_time)
            correct_datetime = timezone.make_aware(correct_datetime)
            
            digest.reminder_time = correct_datetime
            digest.is_sent = False
            digest.save()
            
            print(f"   ✅ Fixed digest time to {target_time.strftime('%I:%M %p')}")
        else:
            print(f"   ✅ Digest time is correct")
    else:
        print(f"📝 No digest found - will be created on next visit")

def check_india_time_status():
    """Check current India time and email status"""
    
    print(f"\n🇮🇳 INDIA TIME STATUS")
    print("=" * 25)
    
    # Calculate India time
    utc_now = timezone.now()
    india_offset = timedelta(hours=5, minutes=30)
    india_now = utc_now + india_offset
    india_time = india_now.time()
    
    print(f"🕐 Current India time: {india_time.strftime('%I:%M %p')}")
    print(f"🕐 Current UTC time: {utc_now.time().strftime('%I:%M %p')}")
    
    # Check if it's past 10:10 PM in India
    target_time = time(22, 10)  # 10:10 PM
    is_past_time = india_time >= target_time
    
    print(f"⏰ Target time: {target_time.strftime('%I:%M %p')}")
    print(f"📊 Is past 10:10 PM in India: {is_past_time}")
    
    return is_past_time

def setup_frequent_background_service():
    """Setup more frequent background service"""
    
    print(f"\n🤖 BACKGROUND SERVICE SETUP")
    print("=" * 35)
    
    print("📋 Current issue:")
    print("   • Windows Task Scheduler runs only once daily at 6:00 AM")
    print("   • Students set evening preferences (10:10 PM)")
    print("   • No service running to check at 10:10 PM")
    
    print(f"\n🔧 Solutions:")
    print("   1. Set Task Scheduler to run every hour")
    print("   2. Or run every 30 minutes")
    print("   3. Or create a continuous service")
    
    # Create a batch file for frequent running
    batch_content = '''@echo off
echo Running ClassWave Email Service...
cd /d "%~dp0"
python manage.py send_real_daily_digests
echo Email service completed at %date% %time%
'''
    
    try:
        with open('run_email_service_frequent.bat', 'w') as f:
            f.write(batch_content)
        print("✅ Created run_email_service_frequent.bat")
        print("   Use this in Task Scheduler to run every 30 minutes")
    except Exception as e:
        print(f"❌ Error creating batch file: {e}")

def send_email_now_if_due():
    """Send email now if it's due according to India time"""
    
    print(f"\n📤 IMMEDIATE EMAIL SENDING")
    print("=" * 30)
    
    # Check India time
    utc_now = timezone.now()
    india_offset = timedelta(hours=5, minutes=30)
    india_now = utc_now + india_offset
    india_time = india_now.time()
    
    print(f"🇮🇳 Current India time: {india_time.strftime('%I:%M %p')}")
    
    # Find students with evening preferences who haven't received emails
    evening_prefs = DailyDigestPreference.objects.filter(
        digest_time__hour__gte=20,  # 8 PM or later
        is_enabled=True
    )
    
    sent_count = 0
    
    for pref in evening_prefs:
        student = pref.student
        pref_time = pref.digest_time
        
        # Check if current India time is past their preference
        if india_time >= pref_time:
            # Find unsent digest
            today = date.today()
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=today,
                is_sent=False
            ).first()
            
            if digest:
                try:
                    from django.core.mail import send_mail
                    
                    print(f"📧 Sending to {student.username} (pref: {pref_time.strftime('%I:%M %p')})...")
                    
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
                    
                    print(f"   ✅ Email sent to {student.email}")
                    sent_count += 1
                    
                except Exception as e:
                    print(f"   ❌ Failed to send to {student.email}: {e}")
    
    print(f"\n📊 Sent {sent_count} emails based on India time")
    return sent_count

def create_continuous_email_service():
    """Create a Python script that runs continuously"""
    
    print(f"\n🔄 CONTINUOUS EMAIL SERVICE")
    print("=" * 35)
    
    service_script = '''#!/usr/bin/env python3
"""
Continuous email service that checks every 5 minutes
"""

import os
import sys
import django
import time
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.core.management import call_command

def run_continuous_service():
    """Run email service continuously"""
    
    print("🤖 Starting continuous email service...")
    print("   Checking every 5 minutes for due emails")
    print("   Press Ctrl+C to stop")
    
    try:
        while True:
            try:
                # Run the email sending command
                call_command('send_real_daily_digests')
                
                # Wait 5 minutes
                print(f"⏰ Next check in 5 minutes... ({datetime.now().strftime('%I:%M %p')})")
                time.sleep(300)  # 5 minutes
                
            except KeyboardInterrupt:
                print("\\n🛑 Service stopped by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("⏳ Continuing in 5 minutes...")
                time.sleep(300)
    
    except KeyboardInterrupt:
        print("\\n🛑 Service stopped")

if __name__ == "__main__":
    run_continuous_service()
'''
    
    try:
        with open('continuous_email_service.py', 'w') as f:
            f.write(service_script)
        print("✅ Created continuous_email_service.py")
        print("   Run: python continuous_email_service.py")
        print("   This will check for emails every 5 minutes")
    except Exception as e:
        print(f"❌ Error creating service script: {e}")

if __name__ == "__main__":
    # Step 1: Check timezone settings
    fix_timezone_in_settings()
    
    # Step 2: Check current digest with new time
    check_current_digest_with_new_time()
    
    # Step 3: Check India time status
    is_due = check_india_time_status()
    
    # Step 4: Setup frequent background service
    setup_frequent_background_service()
    
    # Step 5: Create continuous service
    create_continuous_email_service()
    
    # Step 6: Send emails if due now
    if is_due:
        print(f"\n" + "=" * 50)
        response = input("🤔 Send emails now (past 10:10 PM India time)? (y/n): ")
        if response.lower() == 'y':
            sent = send_email_now_if_due()
            if sent > 0:
                print("🎉 Emails sent according to India time!")
    
    print(f"\n" + "=" * 50)
    print("🎯 COMPLETE SOLUTION:")
    print("   1. Fix Django timezone to 'Asia/Kolkata'")
    print("   2. Run: python continuous_email_service.py")
    print("   3. Or setup Task Scheduler to run every 30 minutes")
    print("   4. Emails will be sent at exact India times!")
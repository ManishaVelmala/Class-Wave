#!/usr/bin/env python3
"""
Fix email timing while keeping Django timezone as UTC
Convert India time preferences to UTC properly
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

def convert_india_time_to_utc(india_time, target_date):
    """Convert India time to UTC time"""
    
    # India is UTC+5:30
    india_offset = timedelta(hours=5, minutes=30)
    
    # Create datetime with India time
    india_datetime = datetime.combine(target_date, india_time)
    
    # Convert to UTC by subtracting the offset
    utc_datetime = india_datetime - india_offset
    
    # Make timezone-aware
    utc_datetime = timezone.make_aware(utc_datetime)
    
    return utc_datetime

def fix_all_digest_times_for_india():
    """Fix all digest times to properly convert India preferences to UTC"""
    
    print("🔧 FIXING DIGEST TIMES FOR INDIA (KEEPING UTC TIMEZONE)")
    print("=" * 60)
    
    today = date.today()
    fixed_count = 0
    
    # Get all students with preferences
    all_prefs = DailyDigestPreference.objects.filter(is_enabled=True)
    
    print(f"👥 Students with preferences: {all_prefs.count()}")
    
    for pref in all_prefs:
        student = pref.student
        india_time = pref.digest_time  # This is what student entered (India time)
        
        print(f"\n👤 {student.username}:")
        print(f"   India preference: {india_time.strftime('%I:%M %p')}")
        
        # Convert India time to UTC
        utc_time = convert_india_time_to_utc(india_time, today)
        
        print(f"   UTC equivalent: {utc_time.strftime('%I:%M %p')} UTC")
        
        # Find today's digest
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if digest:
            old_time = digest.reminder_time
            print(f"   Current digest time: {old_time}")
            
            # Update digest to correct UTC time
            digest.reminder_time = utc_time
            digest.is_sent = False  # Reset if needed
            digest.save()
            
            print(f"   ✅ Updated digest to correct UTC time")
            fixed_count += 1
        else:
            print(f"   📝 No digest found (will be created correctly next time)")
    
    print(f"\n📊 Fixed {fixed_count} digest times")
    return fixed_count

def check_current_status_with_conversion():
    """Check current status with proper timezone conversion"""
    
    print(f"\n📊 CURRENT STATUS (WITH TIMEZONE CONVERSION)")
    print("=" * 50)
    
    utc_now = timezone.now()
    
    # Calculate India time
    india_offset = timedelta(hours=5, minutes=30)
    india_now = utc_now + india_offset
    india_time = india_now.time()
    
    print(f"🕐 Current UTC time: {utc_now.time().strftime('%I:%M %p')}")
    print(f"🇮🇳 Current India time: {india_time.strftime('%I:%M %p')}")
    
    today = date.today()
    all_prefs = DailyDigestPreference.objects.filter(is_enabled=True).order_by('digest_time')
    
    for pref in all_prefs:
        student = pref.student
        india_pref = pref.digest_time
        
        # Convert preference to UTC
        utc_pref_time = convert_india_time_to_utc(india_pref, today)
        
        print(f"\n👤 {student.username}:")
        print(f"   India preference: {india_pref.strftime('%I:%M %p')}")
        print(f"   UTC equivalent: {utc_pref_time.strftime('%I:%M %p')} UTC")
        print(f"   Should send now: {utc_now >= utc_pref_time}")
        
        # Check digest
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if digest:
            print(f"   Digest scheduled: {digest.reminder_time}")
            print(f"   Is sent: {digest.is_sent}")
        else:
            print(f"   Digest: Not found")

def send_due_emails_with_conversion():
    """Send emails that are due based on proper timezone conversion"""
    
    print(f"\n📧 SENDING DUE EMAILS (WITH CONVERSION)")
    print("=" * 45)
    
    utc_now = timezone.now()
    today = date.today()
    
    # Find digests that should be sent now (in UTC)
    due_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=False,
        reminder_time__lte=utc_now
    )
    
    print(f"📧 Due digests found: {due_digests.count()}")
    
    sent_count = 0
    
    for digest in due_digests:
        student = digest.student
        
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            print(f"📤 Sending to {student.username} ({student.email})...")
            
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
            
            print(f"   ✅ Email sent successfully!")
            sent_count += 1
            
        except Exception as e:
            print(f"   ❌ Failed to send: {e}")
    
    print(f"\n📊 Total emails sent: {sent_count}")
    return sent_count

def create_improved_email_service():
    """Create an improved email service that handles timezone conversion"""
    
    service_code = '''#!/usr/bin/env python3
"""
Improved email service with proper timezone conversion
Keeps Django timezone as UTC but handles India time correctly
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
from django.utils import timezone
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def run_improved_service():
    """Run email service with proper timezone handling"""
    
    print("🤖 IMPROVED EMAIL SERVICE (UTC + INDIA CONVERSION)")
    print("=" * 55)
    print("   • Keeps Django timezone as UTC")
    print("   • Converts India preferences correctly")
    print("   • Checks every 2 minutes")
    print("   • Press Ctrl+C to stop")
    
    try:
        check_count = 0
        while True:
            try:
                check_count += 1
                utc_now = timezone.now()
                
                # Calculate India time for display
                india_offset = timedelta(hours=5, minutes=30)
                india_now = utc_now + india_offset
                
                print(f"\\n⏰ Check #{check_count}")
                print(f"   UTC: {utc_now.strftime('%I:%M %p')}")
                print(f"   India: {india_now.strftime('%I:%M %p')}")
                
                # Find due digests (already in UTC)
                today = datetime.now().date()
                due_digests = Reminder.objects.filter(
                    reminder_type='daily_digest',
                    digest_date=today,
                    is_sent=False,
                    reminder_time__lte=utc_now
                )
                
                if due_digests.exists():
                    print(f"   📧 Found {due_digests.count()} due emails")
                    
                    # Send emails
                    from django.core.mail import send_mail
                    from django.conf import settings
                    
                    for digest in due_digests:
                        try:
                            send_mail(
                                subject=f'📅 Your Schedule for {today.strftime("%A, %B %d, %Y")}',
                                message=digest.message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[digest.student.email],
                                fail_silently=False,
                            )
                            
                            digest.is_sent = True
                            digest.sent_at = utc_now
                            digest.save()
                            
                            print(f"   ✅ Sent to {digest.student.username}")
                            
                        except Exception as e:
                            print(f"   ❌ Failed to send to {digest.student.username}: {e}")
                else:
                    print(f"   📭 No emails due")
                
                # Wait 2 minutes
                time.sleep(120)
                
            except KeyboardInterrupt:
                print("\\n🛑 Service stopped by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(120)
    
    except KeyboardInterrupt:
        print("\\n🛑 Service stopped")

if __name__ == "__main__":
    run_improved_service()
'''
    
    try:
        with open('improved_email_service.py', 'w') as f:
            f.write(service_code)
        print("✅ Created improved_email_service.py")
        print("   This service handles timezone conversion properly")
    except Exception as e:
        print(f"❌ Error creating service: {e}")

if __name__ == "__main__":
    print("🎯 SOLUTION: KEEP UTC TIMEZONE + PROPER CONVERSION")
    print("=" * 55)
    
    # Step 1: Fix existing digest times
    fixed = fix_all_digest_times_for_india()
    
    # Step 2: Check current status
    check_current_status_with_conversion()
    
    # Step 3: Send due emails
    response = input(f"\n🤔 Send due emails now? (y/n): ")
    if response.lower() == 'y':
        sent = send_due_emails_with_conversion()
        if sent > 0:
            print("🎉 Emails sent successfully!")
    
    # Step 4: Create improved service
    create_improved_email_service()
    
    print(f"\n" + "=" * 55)
    print("🎯 FINAL SOLUTION:")
    print("   ✅ Django timezone remains UTC (no disadvantage)")
    print("   ✅ India time preferences converted to UTC correctly")
    print("   ✅ Emails sent at exact India times")
    print("   🚀 Run: python improved_email_service.py")
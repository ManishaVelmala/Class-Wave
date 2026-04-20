#!/usr/bin/env python3
"""
Check timezone issue - system using UTC but user is in India (IST)
"""

import os
import sys
import django
from datetime import date, time, datetime, timedelta
from django.utils import timezone
import pytz

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference
from django.conf import settings

def check_timezone_issue():
    """Check timezone settings and current time differences"""
    
    print("🌍 TIMEZONE DIAGNOSTIC")
    print("=" * 30)
    
    # Check Django timezone setting
    print(f"⚙️  Django TIME_ZONE setting: {settings.TIME_ZONE}")
    print(f"⚙️  Django USE_TZ setting: {settings.USE_TZ}")
    
    # Get current times
    utc_now = timezone.now()
    
    # India timezone (IST = UTC+5:30)
    ist_tz = pytz.timezone('Asia/Kolkata')
    ist_now = utc_now.astimezone(ist_tz)
    
    print(f"\n🕐 Current times:")
    print(f"   UTC time: {utc_now.strftime('%Y-%m-%d %I:%M %p %Z')}")
    print(f"   India time (IST): {ist_now.strftime('%Y-%m-%d %I:%M %p %Z')}")
    
    # Calculate difference
    time_diff = ist_now - utc_now.replace(tzinfo=None)
    print(f"   Time difference: {time_diff}")
    
    # Check if it's currently past 9:59 PM in India
    ist_time_only = ist_now.time()
    target_time = time(21, 59)  # 9:59 PM
    
    print(f"\n📊 Time comparison:")
    print(f"   Current IST time: {ist_time_only.strftime('%I:%M %p')}")
    print(f"   Target time (9:59 PM): {target_time.strftime('%I:%M %p')}")
    print(f"   Is past 9:59 PM in India: {ist_time_only >= target_time}")

def check_vaishnavi_digest_with_timezone():
    """Check Vaishnavi's digest considering timezone"""
    
    print(f"\n👤 VAISHNAVI'S DIGEST WITH TIMEZONE")
    print("=" * 40)
    
    # Find Vaishnavi
    vaishnavi = User.objects.filter(username='Vaishnavi').first()
    if not vaishnavi:
        print("❌ Vaishnavi not found")
        return
    
    # Get her digest
    today = date.today()
    digest = Reminder.objects.filter(
        student=vaishnavi,
        reminder_type='daily_digest',
        digest_date=today
    ).first()
    
    if not digest:
        print("❌ No digest found")
        return
    
    print(f"📝 Digest details:")
    print(f"   Scheduled time (UTC): {digest.reminder_time}")
    print(f"   Is sent: {digest.is_sent}")
    
    # Convert to IST
    ist_tz = pytz.timezone('Asia/Kolkata')
    digest_ist = digest.reminder_time.astimezone(ist_tz)
    
    print(f"   Scheduled time (IST): {digest_ist.strftime('%Y-%m-%d %I:%M %p %Z')}")
    
    # Check current time in both zones
    utc_now = timezone.now()
    ist_now = utc_now.astimezone(ist_tz)
    
    print(f"\n🕐 Current times:")
    print(f"   UTC: {utc_now.strftime('%I:%M %p')}")
    print(f"   IST: {ist_now.strftime('%I:%M %p')}")
    
    # Check if email should be sent based on IST
    should_send_utc = digest.reminder_time <= utc_now
    should_send_ist = digest_ist <= ist_now
    
    print(f"\n📧 Should send email:")
    print(f"   Based on UTC: {should_send_utc}")
    print(f"   Based on IST: {should_send_ist}")
    
    if should_send_ist and not digest.is_sent:
        print(f"   ⚠️  EMAIL SHOULD BE SENT NOW (IST time has passed)!")

def fix_timezone_for_india():
    """Suggest timezone fix for India"""
    
    print(f"\n🔧 TIMEZONE FIX FOR INDIA")
    print("=" * 30)
    
    print("📋 Current issue:")
    print("   • System uses UTC timezone")
    print("   • User is in India (IST = UTC+5:30)")
    print("   • 9:59 PM IST = 4:29 PM UTC")
    print("   • Email scheduled for 9:59 PM UTC instead of 9:59 PM IST")
    
    print(f"\n🔧 Solutions:")
    print("   1. Change Django TIME_ZONE to 'Asia/Kolkata'")
    print("   2. Or convert user input to UTC when saving")
    print("   3. Or display times in user's timezone")
    
    # Check what time 9:59 PM IST is in UTC
    ist_tz = pytz.timezone('Asia/Kolkata')
    utc_tz = pytz.UTC
    
    # Create 9:59 PM IST today
    today = date.today()
    ist_959pm = ist_tz.localize(datetime.combine(today, time(21, 59)))
    utc_959pm = ist_959pm.astimezone(utc_tz)
    
    print(f"\n⏰ Time conversion:")
    print(f"   9:59 PM IST = {utc_959pm.strftime('%I:%M %p')} UTC")
    print(f"   Current digest is scheduled for 9:59 PM UTC")
    print(f"   Should be scheduled for {utc_959pm.strftime('%I:%M %p')} UTC")

def send_email_now_if_due():
    """Send email now if it's past 9:59 PM IST"""
    
    print(f"\n📤 MANUAL EMAIL SENDING")
    print("=" * 30)
    
    # Check if it's past 9:59 PM in India
    utc_now = timezone.now()
    ist_tz = pytz.timezone('Asia/Kolkata')
    ist_now = utc_now.astimezone(ist_tz)
    ist_time = ist_now.time()
    
    if ist_time >= time(21, 59):  # Past 9:59 PM IST
        print("🕘 It's past 9:59 PM in India - sending email now!")
        
        # Find Vaishnavi's unsent digest
        vaishnavi = User.objects.filter(username='Vaishnavi').first()
        if vaishnavi:
            today = date.today()
            digest = Reminder.objects.filter(
                student=vaishnavi,
                reminder_type='daily_digest',
                digest_date=today,
                is_sent=False
            ).first()
            
            if digest:
                try:
                    from django.core.mail import send_mail
                    from django.conf import settings
                    
                    print(f"📧 Sending email to {vaishnavi.email}...")
                    
                    send_mail(
                        subject=f'📅 Your Schedule for {today.strftime("%A, %B %d, %Y")}',
                        message=digest.message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[vaishnavi.email],
                        fail_silently=False,
                    )
                    
                    # Mark as sent
                    digest.is_sent = True
                    digest.sent_at = utc_now
                    digest.save()
                    
                    print(f"✅ Email sent successfully!")
                    
                except Exception as e:
                    print(f"❌ Email sending failed: {e}")
            else:
                print("📭 No unsent digest found")
        else:
            print("❌ Vaishnavi not found")
    else:
        print(f"⏳ It's only {ist_time.strftime('%I:%M %p')} in India - not time yet")

if __name__ == "__main__":
    check_timezone_issue()
    check_vaishnavi_digest_with_timezone()
    fix_timezone_for_india()
    
    print(f"\n" + "=" * 50)
    response = input("🤔 Do you want to send the email now (if due in IST)? (y/n): ")
    if response.lower() == 'y':
        send_email_now_if_due()
    
    print(f"\n🎯 SUMMARY:")
    print("   The system is using UTC but you're in India (IST)")
    print("   This causes a 5.5 hour time difference")
    print("   Email should be sent when it's 9:59 PM in India, not UTC")
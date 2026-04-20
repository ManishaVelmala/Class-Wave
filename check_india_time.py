#!/usr/bin/env python3
"""
Check India time issue - simple version without pytz
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

def check_india_time_issue():
    """Check timezone issue for India"""
    
    print("🇮🇳 INDIA TIMEZONE CHECK")
    print("=" * 30)
    
    # Get current UTC time
    utc_now = timezone.now()
    
    # Calculate India time (UTC + 5:30)
    india_offset = timedelta(hours=5, minutes=30)
    india_now = utc_now + india_offset
    
    print(f"🕐 Current times:")
    print(f"   UTC time: {utc_now.strftime('%Y-%m-%d %I:%M %p')}")
    print(f"   India time (IST): {india_now.strftime('%Y-%m-%d %I:%M %p')}")
    
    # Check if it's past 9:59 PM in India
    india_time_only = india_now.time()
    target_time = time(21, 59)  # 9:59 PM
    
    print(f"\n📊 Time comparison:")
    print(f"   Current India time: {india_time_only.strftime('%I:%M %p')}")
    print(f"   Target time: {target_time.strftime('%I:%M %p')}")
    print(f"   Is past 9:59 PM in India: {india_time_only >= target_time}")
    
    return india_time_only >= target_time

def check_vaishnavi_digest_india_time():
    """Check Vaishnavi's digest with India time"""
    
    print(f"\n👤 VAISHNAVI'S DIGEST (INDIA TIME)")
    print("=" * 35)
    
    # Find Vaishnavi
    vaishnavi = User.objects.filter(username='Vaishnavi').first()
    if not vaishnavi:
        print("❌ Vaishnavi not found")
        return False
    
    # Get her digest
    today = date.today()
    digest = Reminder.objects.filter(
        student=vaishnavi,
        reminder_type='daily_digest',
        digest_date=today
    ).first()
    
    if not digest:
        print("❌ No digest found")
        return False
    
    print(f"📝 Digest details:")
    print(f"   Scheduled (UTC): {digest.reminder_time}")
    print(f"   Is sent: {digest.is_sent}")
    
    # Convert digest time to India time
    india_offset = timedelta(hours=5, minutes=30)
    digest_india_time = digest.reminder_time + india_offset
    
    print(f"   Scheduled (India): {digest_india_time.strftime('%Y-%m-%d %I:%M %p')}")
    
    # Get current times
    utc_now = timezone.now()
    india_now = utc_now + india_offset
    
    print(f"\n🕐 Current times:")
    print(f"   UTC: {utc_now.strftime('%I:%M %p')}")
    print(f"   India: {india_now.strftime('%I:%M %p')}")
    
    # Check if email should be sent
    should_send_utc = digest.reminder_time <= utc_now
    should_send_india = digest_india_time <= india_now
    
    print(f"\n📧 Should send email:")
    print(f"   Based on UTC: {should_send_utc}")
    print(f"   Based on India time: {should_send_india}")
    
    if should_send_india and not digest.is_sent:
        print(f"   ⚠️  EMAIL SHOULD BE SENT NOW (India time has passed)!")
        return True
    
    return False

def explain_timezone_problem():
    """Explain the timezone problem"""
    
    print(f"\n🔍 TIMEZONE PROBLEM EXPLANATION")
    print("=" * 40)
    
    print("📋 The issue:")
    print("   • Student set preference: 9:59 PM (thinking India time)")
    print("   • System saved it as: 9:59 PM UTC")
    print("   • 9:59 PM UTC = 3:29 AM India time (next day)")
    print("   • 9:59 PM India time = 4:29 PM UTC")
    
    # Calculate what time 9:59 PM India is in UTC
    india_offset = timedelta(hours=5, minutes=30)
    
    # 9:59 PM India time
    today = date.today()
    india_959pm = datetime.combine(today, time(21, 59))
    
    # Convert to UTC (subtract 5:30)
    utc_equivalent = india_959pm - india_offset
    
    print(f"\n⏰ Correct conversion:")
    print(f"   9:59 PM India time = {utc_equivalent.strftime('%I:%M %p')} UTC")
    print(f"   Current digest is scheduled for 9:59 PM UTC")
    print(f"   Should be scheduled for {utc_equivalent.strftime('%I:%M %p')} UTC")

def send_email_if_due_india():
    """Send email if it's due according to India time"""
    
    print(f"\n📤 SENDING EMAIL (INDIA TIME CHECK)")
    print("=" * 40)
    
    # Check if it's past 9:59 PM in India
    utc_now = timezone.now()
    india_offset = timedelta(hours=5, minutes=30)
    india_now = utc_now + india_offset
    india_time = india_now.time()
    
    print(f"🇮🇳 Current India time: {india_time.strftime('%I:%M %p')}")
    
    if india_time >= time(21, 59):  # Past 9:59 PM India time
        print("✅ It's past 9:59 PM in India - sending email now!")
        
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
                    
                    print(f"✅ Email sent successfully to India!")
                    return True
                    
                except Exception as e:
                    print(f"❌ Email sending failed: {e}")
                    return False
            else:
                print("📭 No unsent digest found")
                return False
        else:
            print("❌ Vaishnavi not found")
            return False
    else:
        print(f"⏳ It's only {india_time.strftime('%I:%M %p')} in India - not time yet")
        return False

if __name__ == "__main__":
    # Check if it's past 9:59 PM in India
    is_due_india = check_india_time_issue()
    
    # Check Vaishnavi's digest
    should_send = check_vaishnavi_digest_india_time()
    
    # Explain the problem
    explain_timezone_problem()
    
    # Send email if due
    if is_due_india or should_send:
        print(f"\n" + "=" * 40)
        response = input("🤔 Send email now (it's past 9:59 PM India time)? (y/n): ")
        if response.lower() == 'y':
            sent = send_email_if_due_india()
            if sent:
                print("🎉 Email sent according to India time!")
    else:
        print(f"\n⏳ Email will be sent when it's 9:59 PM in India")
    
    print(f"\n🎯 SOLUTION NEEDED:")
    print("   Fix timezone handling to use India time (IST)")
    print("   Or convert user preferences to UTC correctly")
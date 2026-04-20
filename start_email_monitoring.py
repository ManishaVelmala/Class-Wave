#!/usr/bin/env python3
"""
Start email monitoring service that will send emails at the correct times
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

def start_monitoring():
    """Start continuous email monitoring"""
    
    print("🤖 STARTING EMAIL MONITORING SERVICE")
    print("=" * 45)
    print("   • Checking every 2 minutes for due emails")
    print("   • Using India timezone (Asia/Kolkata)")
    print("   • Press Ctrl+C to stop")
    
    # Show next email to be sent
    from accounts.models import User
    from reminders.models import Reminder, DailyDigestPreference
    from datetime import date
    
    now = timezone.now()
    current_time = now.time()
    today = date.today()
    
    print(f"\n📊 Current status:")
    print(f"   🕐 Current time: {current_time.strftime('%I:%M %p')} India")
    print(f"   📅 Date: {today}")
    
    # Find next email to be sent
    next_email = None
    next_time = None
    
    all_prefs = DailyDigestPreference.objects.filter(is_enabled=True).order_by('digest_time')
    
    for pref in all_prefs:
        if current_time < pref.digest_time:
            # Check if they have an unsent digest
            digest = Reminder.objects.filter(
                student=pref.student,
                reminder_type='daily_digest',
                digest_date=today,
                is_sent=False
            ).first()
            
            if digest:
                next_email = pref.student.username
                next_time = pref.digest_time
                break
    
    if next_email:
        print(f"   📧 Next email: {next_email} at {next_time.strftime('%I:%M %p')}")
        
        # Calculate time until next email
        next_datetime = datetime.combine(today, next_time)
        current_datetime = datetime.combine(today, current_time)
        time_diff = next_datetime - current_datetime
        
        hours = int(time_diff.total_seconds() // 3600)
        minutes = int((time_diff.total_seconds() % 3600) // 60)
        
        print(f"   ⏳ Time until next email: {hours}h {minutes}m")
    else:
        print(f"   📭 No more emails scheduled for today")
    
    print(f"\n🚀 Starting monitoring...")
    
    try:
        check_count = 0
        while True:
            try:
                check_count += 1
                current_time = timezone.now()
                
                print(f"\n⏰ Check #{check_count} at {current_time.strftime('%I:%M %p')} India")
                
                # Run the email sending command
                call_command('send_real_daily_digests')
                
                # Also run our custom sender for India time
                from send_email_now import send_email_now
                sent = send_email_now()
                
                if sent > 0:
                    print(f"🎉 Sent {sent} emails!")
                else:
                    print("📭 No emails due yet")
                
                # Wait 2 minutes
                print(f"⏳ Next check in 2 minutes...")
                time.sleep(120)  # 2 minutes
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("⏳ Continuing in 2 minutes...")
                time.sleep(120)
    
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")

if __name__ == "__main__":
    start_monitoring()
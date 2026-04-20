#!/usr/bin/env python3
"""
Email Service Dashboard - Real-time monitoring
Shows live status of email service and upcoming emails
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

from django.utils import timezone
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_live_status():
    """Get live status of the email service"""
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    current_time = india_now.time()
    
    students = User.objects.filter(user_type='student')
    sent_today = 0
    pending_today = 0
    upcoming_emails = []
    
    for student in students:
        try:
            pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=india_date
            ).first()
            
            if digest and digest.is_sent:
                sent_today += 1
            else:
                pending_today += 1
                
                # Calculate time until email
                pref_datetime = datetime.combine(india_date, pref.digest_time)
                current_datetime = datetime.combine(india_date, current_time)
                
                if pref_datetime > current_datetime:
                    time_until = pref_datetime - current_datetime
                    hours_until = time_until.total_seconds() / 3600
                    
                    upcoming_emails.append({
                        'student': student.username,
                        'time': pref.digest_time,
                        'hours_until': hours_until
                    })
                    
        except DailyDigestPreference.DoesNotExist:
            continue
    
    upcoming_emails.sort(key=lambda x: x['hours_until'])
    
    return {
        'current_time': current_time,
        'current_date': india_date,
        'sent_today': sent_today,
        'pending_today': pending_today,
        'upcoming_emails': upcoming_emails
    }

def display_dashboard():
    """Display the live dashboard"""
    
    status = get_live_status()
    
    print("=" * 60)
    print("           📧 EMAIL SERVICE LIVE DASHBOARD 📧")
    print("=" * 60)
    
    print(f"🕐 Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🇮🇳 India Time:   {status['current_time'].strftime('%I:%M %p')}")
    print(f"📅 Date:         {status['current_date']}")
    
    print(f"\n📊 TODAY'S EMAIL STATISTICS")
    print(f"   ✅ Emails Sent:    {status['sent_today']}")
    print(f"   ⏳ Emails Pending: {status['pending_today']}")
    
    if status['upcoming_emails']:
        print(f"\n⏰ UPCOMING EMAILS")
        print(f"   {'Student':<15} {'Time':<10} {'Countdown':<15}")
        print(f"   {'-'*15} {'-'*10} {'-'*15}")
        
        for email in status['upcoming_emails']:
            if email['hours_until'] < 1:
                countdown = f"{email['hours_until']*60:.0f} minutes"
            elif email['hours_until'] < 24:
                countdown = f"{email['hours_until']:.1f} hours"
            else:
                countdown = f"{email['hours_until']/24:.1f} days"
            
            print(f"   {email['student']:<15} {email['time'].strftime('%I:%M %p'):<10} {countdown:<15}")
    else:
        print(f"\n✅ ALL EMAILS SENT FOR TODAY!")
    
    # Next email highlight
    if status['upcoming_emails']:
        next_email = status['upcoming_emails'][0]
        print(f"\n🎯 NEXT EMAIL:")
        if next_email['hours_until'] < 1:
            minutes = next_email['hours_until'] * 60
            print(f"   📧 {next_email['student']} in {minutes:.0f} minutes at {next_email['time'].strftime('%I:%M %p')}")
        else:
            print(f"   📧 {next_email['student']} in {next_email['hours_until']:.1f} hours at {next_email['time'].strftime('%I:%M %p')}")
    
    print(f"\n🤖 SERVICE STATUS:")
    print(f"   🟢 Background service should be running")
    print(f"   🔄 Checks every 30 seconds for due emails")
    print(f"   ⚡ Emails sent within 30 seconds of preference time")
    
    print(f"\n💡 CONTROLS:")
    print(f"   Press Ctrl+C to exit dashboard")
    print(f"   Dashboard updates every 30 seconds")
    
    print("=" * 60)

def run_live_dashboard():
    """Run the live dashboard with auto-refresh"""
    
    try:
        while True:
            clear_screen()
            display_dashboard()
            time.sleep(30)  # Update every 30 seconds
            
    except KeyboardInterrupt:
        clear_screen()
        print("📊 EMAIL SERVICE DASHBOARD CLOSED")
        print("=" * 35)
        print("Dashboard stopped by user")

def main():
    """Main function"""
    
    print("📊 EMAIL SERVICE DASHBOARD")
    print("=" * 27)
    print("This will show live status of the email service")
    print("Updates every 30 seconds")
    print()
    
    input("Press Enter to start live dashboard...")
    
    run_live_dashboard()

if __name__ == "__main__":
    main()
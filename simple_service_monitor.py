#!/usr/bin/env python3
"""
Simple Service Monitor - No external dependencies
Checks if email service is working by monitoring email delivery
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

def check_service_health():
    """Check if the email service is working properly"""
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    current_time = india_now.time()
    
    print(f"🔍 EMAIL SERVICE HEALTH CHECK")
    print(f"=" * 30)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"India Time: {current_time.strftime('%I:%M %p')}")
    
    # Check email statistics
    students = User.objects.filter(user_type='student')
    sent_today = 0
    pending_today = 0
    overdue_emails = []
    upcoming_emails = []
    timing_issues = []
    
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
                
                # Check timing accuracy
                sent_time = (digest.sent_at + timedelta(hours=5, minutes=30)).time()
                pref_time = pref.digest_time
                
                if sent_time < pref_time:
                    time_diff = datetime.combine(india_date, pref_time) - datetime.combine(india_date, sent_time)
                    hours_early = time_diff.total_seconds() / 3600
                    
                    if hours_early > 2:  # More than 2 hours early
                        timing_issues.append({
                            'student': student.username,
                            'preference': pref_time,
                            'sent': sent_time,
                            'hours_early': hours_early
                        })
            else:
                pending_today += 1
                
                # Check if email is overdue
                pref_datetime = datetime.combine(india_date, pref.digest_time)
                current_datetime = datetime.combine(india_date, current_time)
                
                if current_datetime > pref_datetime:
                    # Email is overdue
                    time_overdue = current_datetime - pref_datetime
                    hours_overdue = time_overdue.total_seconds() / 3600
                    
                    overdue_emails.append({
                        'student': student.username,
                        'preference': pref.digest_time,
                        'hours_overdue': hours_overdue
                    })
                else:
                    # Email is upcoming
                    time_until = pref_datetime - current_datetime
                    hours_until = time_until.total_seconds() / 3600
                    
                    upcoming_emails.append({
                        'student': student.username,
                        'preference': pref.digest_time,
                        'hours_until': hours_until
                    })
                    
        except DailyDigestPreference.DoesNotExist:
            continue
    
    # Print results
    print(f"\n📊 EMAIL STATISTICS:")
    print(f"   ✅ Sent today: {sent_today}")
    print(f"   ⏳ Pending: {pending_today}")
    
    # Check for issues
    issues_found = 0
    
    if overdue_emails:
        print(f"\n🚨 OVERDUE EMAILS ({len(overdue_emails)}):")
        issues_found += len(overdue_emails)
        for email in overdue_emails:
            print(f"   ❌ {email['student']}: {email['hours_overdue']:.1f}h overdue (should have sent at {email['preference'].strftime('%I:%M %p')})")
    
    if timing_issues:
        print(f"\n⚠️  TIMING ISSUES ({len(timing_issues)}):")
        issues_found += len(timing_issues)
        for issue in timing_issues:
            print(f"   🚨 {issue['student']}: Sent {issue['hours_early']:.1f}h early")
    
    if upcoming_emails:
        print(f"\n⏰ UPCOMING EMAILS ({len(upcoming_emails)}):")
        upcoming_emails.sort(key=lambda x: x['hours_until'])
        for email in upcoming_emails[:3]:  # Show next 3
            if email['hours_until'] < 1:
                minutes = email['hours_until'] * 60
                print(f"   📧 {email['student']}: in {minutes:.0f} minutes at {email['preference'].strftime('%I:%M %p')}")
            else:
                print(f"   📧 {email['student']}: in {email['hours_until']:.1f}h at {email['preference'].strftime('%I:%M %p')}")
    
    # Overall health assessment
    print(f"\n🏥 HEALTH ASSESSMENT:")
    if issues_found == 0 and overdue_emails == []:
        print(f"   ✅ HEALTHY - Service working correctly")
        health_status = "HEALTHY"
    elif overdue_emails:
        print(f"   🚨 CRITICAL - {len(overdue_emails)} overdue emails")
        print(f"   💡 Email service may not be running!")
        health_status = "CRITICAL"
    else:
        print(f"   ⚠️  WARNING - {issues_found} timing issues")
        health_status = "WARNING"
    
    return {
        'health_status': health_status,
        'sent_today': sent_today,
        'pending_today': pending_today,
        'overdue_emails': len(overdue_emails),
        'timing_issues': len(timing_issues),
        'next_email': upcoming_emails[0] if upcoming_emails else None
    }

def check_startup_service():
    """Check if startup service is configured"""
    
    startup_folder = os.path.join(os.environ['APPDATA'], 
                                 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    startup_file = os.path.join(startup_folder, 'ClassWave_Email_Service.bat')
    
    print(f"\n🚀 STARTUP CONFIGURATION:")
    if os.path.exists(startup_file):
        print(f"   ✅ Startup script exists")
        print(f"   📁 Location: {startup_file}")
        print(f"   💡 Service will start automatically on boot")
    else:
        print(f"   ❌ No startup script found")
        print(f"   💡 Run: python setup_automatic_system.py")

def continuous_monitoring():
    """Run continuous monitoring"""
    
    print(f"\n🔄 STARTING CONTINUOUS MONITORING")
    print(f"=" * 35)
    print(f"Checking every 5 minutes")
    print(f"Press Ctrl+C to stop")
    
    try:
        while True:
            result = check_service_health()
            
            if result['health_status'] == 'CRITICAL':
                print(f"\n🚨 CRITICAL ISSUE DETECTED!")
                print(f"💡 Recommended actions:")
                print(f"   1. Check if email service is running")
                print(f"   2. Restart manually: python start_continuous_email_service.py")
                print(f"   3. Check Gmail credentials")
            
            print(f"\n⏰ Next check in 5 minutes...")
            print(f"=" * 40)
            
            time.sleep(300)  # 5 minutes
            
    except KeyboardInterrupt:
        print(f"\n🛑 Monitoring stopped")

def main():
    """Main function"""
    
    # Run initial check
    result = check_service_health()
    
    # Check startup configuration
    check_startup_service()
    
    # Ask for continuous monitoring
    print(f"\n💡 MONITORING OPTIONS:")
    print(f"1. Single check only")
    print(f"2. Continuous monitoring (every 5 minutes)")
    
    choice = input(f"\nEnter choice (1 or 2): ").strip()
    
    if choice == "2":
        continuous_monitoring()
    else:
        print(f"\n✅ Health check complete")
        
        if result['health_status'] == 'CRITICAL':
            print(f"\n⚠️  CRITICAL ISSUES FOUND!")
            print(f"💡 Start email service: python start_continuous_email_service.py")

if __name__ == "__main__":
    main()
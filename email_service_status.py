#!/usr/bin/env python3
"""
Check the status of the email service and upcoming emails
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

def show_email_service_status():
    """Show current email service status and upcoming emails"""
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    current_india_time = india_now.time()
    
    print("📧 EMAIL SERVICE STATUS")
    print("=" * 25)
    print(f"Current India time: {current_india_time.strftime('%I:%M %p')}")
    print(f"Current India date: {india_date}")
    
    # Check if service is running (this is a simple check)
    print(f"\n🤖 BACKGROUND SERVICE:")
    print("   Status: Check if start_continuous_email_service.py is running")
    print("   Purpose: Automatically sends emails at correct times")
    print("   Frequency: Checks every 30 seconds")
    
    students = User.objects.filter(user_type='student')
    
    upcoming_emails = []
    sent_today = []
    
    print(f"\n📋 TODAY'S EMAIL SCHEDULE:")
    print("=" * 27)
    
    for student in students:
        try:
            pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
            student_pref_time = pref.digest_time
            
            # Check if digest exists and is sent
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=india_date
            ).first()
            
            if digest and digest.is_sent:
                sent_time = (digest.sent_at + timedelta(hours=5, minutes=30)).time()
                sent_today.append({
                    'student': student,
                    'preference': student_pref_time,
                    'sent_time': sent_time,
                    'status': 'sent'
                })
            else:
                # Calculate time until email
                pref_datetime = datetime.combine(india_date, student_pref_time)
                current_datetime = datetime.combine(india_date, current_india_time)
                
                if pref_datetime > current_datetime:
                    time_until = pref_datetime - current_datetime
                    hours_until = time_until.total_seconds() / 3600
                    
                    upcoming_emails.append({
                        'student': student,
                        'preference': student_pref_time,
                        'hours_until': hours_until,
                        'status': 'pending'
                    })
                else:
                    # Should have been sent already
                    upcoming_emails.append({
                        'student': student,
                        'preference': student_pref_time,
                        'hours_until': 0,
                        'status': 'overdue'
                    })
                    
        except DailyDigestPreference.DoesNotExist:
            print(f"⚠️  {student.username}: No preference set")
    
    # Sort upcoming emails by time
    upcoming_emails.sort(key=lambda x: x['hours_until'])
    
    # Show sent emails
    if sent_today:
        print(f"\n✅ EMAILS SENT TODAY ({len(sent_today)}):")
        for info in sent_today:
            student = info['student']
            pref_time = info['preference']
            sent_time = info['sent_time']
            
            # Check timing accuracy
            if sent_time >= pref_time:
                timing_status = "✅ On time"
            else:
                time_diff = datetime.combine(india_date, pref_time) - datetime.combine(india_date, sent_time)
                minutes_early = time_diff.total_seconds() / 60
                if minutes_early <= 30:
                    timing_status = "✅ Perfect timing"
                else:
                    timing_status = f"⚠️  {minutes_early:.0f}min early"
            
            print(f"   📧 {student.username}:")
            print(f"      Scheduled: {pref_time.strftime('%I:%M %p')}")
            print(f"      Sent: {sent_time.strftime('%I:%M %p')}")
            print(f"      Status: {timing_status}")
    
    # Show upcoming emails
    if upcoming_emails:
        print(f"\n⏰ UPCOMING EMAILS ({len(upcoming_emails)}):")
        for info in upcoming_emails:
            student = info['student']
            pref_time = info['preference']
            hours_until = info['hours_until']
            status = info['status']
            
            if status == 'overdue':
                print(f"   🚨 {student.username}:")
                print(f"      Scheduled: {pref_time.strftime('%I:%M %p')}")
                print(f"      Status: OVERDUE - should have been sent")
            else:
                print(f"   ⏰ {student.username}:")
                print(f"      Scheduled: {pref_time.strftime('%I:%M %p')}")
                if hours_until < 1:
                    minutes_until = hours_until * 60
                    print(f"      Time until: {minutes_until:.0f} minutes")
                else:
                    print(f"      Time until: {hours_until:.1f} hours")
    
    print(f"\n🎯 NEXT EMAIL:")
    print("=" * 13)
    if upcoming_emails:
        next_email = upcoming_emails[0]
        student = next_email['student']
        pref_time = next_email['preference']
        hours_until = next_email['hours_until']
        
        if hours_until <= 0:
            print(f"   📧 {student.username} - SHOULD SEND NOW!")
        elif hours_until < 1:
            minutes_until = hours_until * 60
            print(f"   📧 {student.username} - in {minutes_until:.0f} minutes at {pref_time.strftime('%I:%M %p')}")
        else:
            print(f"   📧 {student.username} - in {hours_until:.1f} hours at {pref_time.strftime('%I:%M %p')}")
    else:
        print("   ✅ All emails sent for today!")
    
    print(f"\n💡 HOW TO ENSURE EMAILS ARE SENT:")
    print("=" * 33)
    print("   1. Keep the background service running:")
    print("      python start_continuous_email_service.py")
    print("   2. Or use the batch file:")
    print("      start_permanent_email_service.bat")
    print("   3. The service checks every 30 seconds")
    print("   4. Emails are sent within 30 seconds of preference time")

if __name__ == "__main__":
    show_email_service_status()
#!/usr/bin/env python3
"""
Check current timing status - who should get emails now vs who should wait
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

def check_timing_status():
    """Check current timing status for all students"""
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    current_india_time = india_now.time()
    
    print("🕐 CURRENT TIMING STATUS")
    print("=" * 25)
    print(f"Current India time: {current_india_time.strftime('%I:%M %p')}")
    print(f"Current India date: {india_date}")
    
    students = User.objects.filter(user_type='student')
    
    should_send_now = []
    waiting_for_time = []
    already_sent = []
    
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
                already_sent.append({
                    'student': student,
                    'preference': student_pref_time,
                    'sent_time': sent_time
                })
            else:
                # Check if it's time to send
                if current_india_time >= student_pref_time:
                    # Additional safety check
                    time_diff = datetime.combine(india_date, current_india_time) - datetime.combine(india_date, student_pref_time)
                    
                    if time_diff.total_seconds() >= -7200:  # Not more than 2 hours early
                        should_send_now.append({
                            'student': student,
                            'preference': student_pref_time,
                            'digest': digest
                        })
                    else:
                        waiting_for_time.append({
                            'student': student,
                            'preference': student_pref_time,
                            'digest': digest
                        })
                else:
                    waiting_for_time.append({
                        'student': student,
                        'preference': student_pref_time,
                        'digest': digest
                    })
                    
        except DailyDigestPreference.DoesNotExist:
            print(f"⚠️  {student.username}: No preference set")
    
    print(f"\n📧 SHOULD SEND NOW ({len(should_send_now)} students):")
    print("=" * 35)
    for info in should_send_now:
        student = info['student']
        pref_time = info['preference']
        digest = info['digest']
        
        print(f"✅ {student.username}:")
        print(f"   Preference: {pref_time.strftime('%I:%M %p')}")
        print(f"   Status: {'Has digest' if digest else 'No digest created'}")
        print(f"   Action: Should send email NOW")
    
    print(f"\n⏳ WAITING FOR TIME ({len(waiting_for_time)} students):")
    print("=" * 38)
    for info in waiting_for_time:
        student = info['student']
        pref_time = info['preference']
        digest = info['digest']
        
        # Calculate time until email should be sent
        pref_datetime = datetime.combine(india_date, pref_time)
        current_datetime = datetime.combine(india_date, current_india_time)
        
        if pref_datetime > current_datetime:
            time_until = pref_datetime - current_datetime
            hours_until = time_until.total_seconds() / 3600
            
            print(f"⏳ {student.username}:")
            print(f"   Preference: {pref_time.strftime('%I:%M %p')}")
            print(f"   Status: {'Has digest' if digest else 'No digest created'}")
            print(f"   Wait time: {hours_until:.1f} hours")
        else:
            print(f"⏳ {student.username}:")
            print(f"   Preference: {pref_time.strftime('%I:%M %p')}")
            print(f"   Status: {'Has digest' if digest else 'No digest created'}")
            print(f"   Note: Time passed but safety check preventing send")
    
    print(f"\n✅ ALREADY SENT ({len(already_sent)} students):")
    print("=" * 32)
    for info in already_sent:
        student = info['student']
        pref_time = info['preference']
        sent_time = info['sent_time']
        
        # Check if sent at correct time
        if sent_time >= pref_time:
            timing_status = "✅ Correct timing"
        else:
            time_diff = datetime.combine(india_date, pref_time) - datetime.combine(india_date, sent_time)
            hours_early = time_diff.total_seconds() / 3600
            timing_status = f"🚨 {hours_early:.1f}h early"
        
        print(f"📧 {student.username}:")
        print(f"   Preference: {pref_time.strftime('%I:%M %p')}")
        print(f"   Sent: {sent_time.strftime('%I:%M %p')}")
        print(f"   Timing: {timing_status}")
    
    print(f"\n📊 SUMMARY:")
    print("=" * 10)
    print(f"Should send now: {len(should_send_now)}")
    print(f"Waiting for time: {len(waiting_for_time)}")
    print(f"Already sent: {len(already_sent)}")
    
    return should_send_now, waiting_for_time, already_sent

if __name__ == "__main__":
    check_timing_status()
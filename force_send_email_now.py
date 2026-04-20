#!/usr/bin/env python3
"""
Force send email now using correct India time (22:21)
"""

import os
import sys
import django
from datetime import date, time, datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference
from django.conf import settings
from django.utils import timezone

def force_send_email_now():
    """Force send email using correct India time"""
    
    print("🚀 FORCE SENDING EMAIL (INDIA TIME 22:21)")
    print("=" * 50)
    
    # Current India time is 22:21 (10:21 PM)
    india_time = time(22, 21)  # 10:21 PM
    today = date.today()
    
    print(f"🇮🇳 Current India time: {india_time.strftime('%I:%M %p')}")
    print(f"📅 Date: {today}")
    
    # Find students whose preference time has passed
    students_due = []
    all_prefs = DailyDigestPreference.objects.filter(is_enabled=True)
    
    for pref in all_prefs:
        student = pref.student
        pref_time = pref.digest_time
        
        print(f"\n👤 {student.username}:")
        print(f"   Preference: {pref_time.strftime('%I:%M %p')}")
        print(f"   Should send: {india_time >= pref_time}")
        
        if india_time >= pref_time:
            # Check if they have an unsent digest
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=today,
                is_sent=False
            ).first()
            
            if digest:
                students_due.append((student, pref_time, digest))
                print(f"   📧 Ready to send!")
            else:
                print(f"   📭 No unsent digest")
        else:
            print(f"   ⏳ Not time yet")
    
    print(f"\n📊 Students due for email: {len(students_due)}")
    
    if not students_due:
        print("📭 No students are due for email")
        return 0
    
    # Send emails
    sent_count = 0
    current_utc = timezone.now()
    
    for student, pref_time, digest in students_due:
        try:
            from django.core.mail import send_mail
            
            print(f"\n📤 Sending to {student.username} ({student.email})...")
            
            send_mail(
                subject=f'📅 Your Schedule for {today.strftime("%A, %B %d, %Y")}',
                message=digest.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=False,
            )
            
            # Mark as sent
            digest.is_sent = True
            digest.sent_at = current_utc
            digest.save()
            
            print(f"✅ Email sent successfully!")
            sent_count += 1
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
    
    print(f"\n🎉 Total emails sent: {sent_count}")
    return sent_count

def show_all_student_status():
    """Show status of all students"""
    
    print(f"\n📊 ALL STUDENT STATUS")
    print("=" * 25)
    
    india_time = time(22, 21)  # Current India time
    today = date.today()
    
    all_prefs = DailyDigestPreference.objects.filter(is_enabled=True).order_by('digest_time')
    
    for pref in all_prefs:
        student = pref.student
        pref_time = pref.digest_time
        
        # Check digest
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        print(f"\n👤 {student.username}:")
        print(f"   Email: {student.email}")
        print(f"   Preference: {pref_time.strftime('%I:%M %p')}")
        print(f"   Current time: {india_time.strftime('%I:%M %p')}")
        print(f"   Time passed: {india_time >= pref_time}")
        
        if digest:
            print(f"   Digest exists: YES")
            print(f"   Is sent: {digest.is_sent}")
            if digest.sent_at:
                print(f"   Sent at: {digest.sent_at}")
        else:
            print(f"   Digest exists: NO")

if __name__ == "__main__":
    show_all_student_status()
    
    print(f"\n" + "=" * 50)
    print("🎯 ANALYSIS:")
    print("   Current India time: 10:21 PM")
    print("   Student preference: 10:18 PM") 
    print("   Email should be sent: YES (3 minutes late)")
    
    response = input(f"\n🤔 Force send email now? (y/n): ")
    if response.lower() == 'y':
        sent = force_send_email_now()
        if sent > 0:
            print("🎉 Email sent successfully!")
            print("📧 Student should receive email now!")
        else:
            print("📭 No emails were sent")
    
    print(f"\n💡 NOTE:")
    print("   Django timezone change requires server restart")
    print("   This script forces correct India time calculation")
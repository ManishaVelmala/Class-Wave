#!/usr/bin/env python3
"""
Send email immediately for students whose time has passed
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

def send_email_now():
    """Send email immediately for due students"""
    
    print("📧 SENDING EMAILS NOW")
    print("=" * 25)
    
    # Get current time (now using Asia/Kolkata timezone)
    now = timezone.now()
    current_time = now.time()
    today = date.today()
    
    print(f"🕐 Current time (India): {current_time.strftime('%I:%M %p')}")
    print(f"📅 Date: {today}")
    
    # Find students whose time has passed
    due_students = []
    all_prefs = DailyDigestPreference.objects.filter(is_enabled=True)
    
    for pref in all_prefs:
        if current_time >= pref.digest_time:
            # Check if they have an unsent digest
            digest = Reminder.objects.filter(
                student=pref.student,
                reminder_type='daily_digest',
                digest_date=today,
                is_sent=False
            ).first()
            
            if digest:
                due_students.append((pref.student, pref.digest_time, digest))
    
    print(f"\n👥 Students due for email: {len(due_students)}")
    
    sent_count = 0
    
    for student, pref_time, digest in due_students:
        print(f"\n👤 {student.username}:")
        print(f"   Preference: {pref_time.strftime('%I:%M %p')}")
        print(f"   Current time: {current_time.strftime('%I:%M %p')}")
        print(f"   Should send: {current_time >= pref_time}")
        
        try:
            from django.core.mail import send_mail
            
            print(f"   📤 Sending email to {student.email}...")
            
            send_mail(
                subject=f'📅 Your Schedule for {today.strftime("%A, %B %d, %Y")}',
                message=digest.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=False,
            )
            
            # Mark as sent
            digest.is_sent = True
            digest.sent_at = now
            digest.save()
            
            print(f"   ✅ Email sent successfully!")
            sent_count += 1
            
        except Exception as e:
            print(f"   ❌ Failed to send email: {e}")
    
    print(f"\n📊 Total emails sent: {sent_count}")
    
    if sent_count == 0:
        print("📭 No emails were due to be sent")
        print("   Possible reasons:")
        print("   • All digests already sent")
        print("   • No classes scheduled for today")
        print("   • Current time is before preference times")
    
    return sent_count

def check_current_status():
    """Check current status of all students"""
    
    print(f"\n📊 CURRENT STATUS CHECK")
    print("=" * 30)
    
    now = timezone.now()
    current_time = now.time()
    today = date.today()
    
    all_prefs = DailyDigestPreference.objects.filter(is_enabled=True).order_by('digest_time')
    
    for pref in all_prefs:
        student = pref.student
        pref_time = pref.digest_time
        
        # Check digest status
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        print(f"\n👤 {student.username}:")
        print(f"   Preference: {pref_time.strftime('%I:%M %p')}")
        print(f"   Time passed: {current_time >= pref_time}")
        
        if digest:
            print(f"   Digest exists: YES")
            print(f"   Is sent: {digest.is_sent}")
            if digest.sent_at:
                print(f"   Sent at: {digest.sent_at.strftime('%I:%M %p')}")
        else:
            print(f"   Digest exists: NO (no classes today)")

if __name__ == "__main__":
    check_current_status()
    
    print(f"\n" + "=" * 40)
    response = input("🤔 Do you want to send emails now? (y/n): ")
    if response.lower() == 'y':
        sent = send_email_now()
        if sent > 0:
            print("🎉 Emails sent successfully!")
        else:
            print("📭 No emails were sent")
    
    print(f"\n🎯 TO AUTOMATE THIS:")
    print("   Run: python continuous_email_service.py")
    print("   This will check every 5 minutes automatically")
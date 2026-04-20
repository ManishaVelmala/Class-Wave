#!/usr/bin/env python3
"""
Send emails that are due according to India time
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

def send_due_emails_india_time():
    """Send emails based on India time"""
    
    print("📧 SENDING EMAILS BASED ON INDIA TIME")
    print("=" * 45)
    
    # Get current India time
    utc_now = timezone.now()
    india_offset = timedelta(hours=5, minutes=30)
    india_now = utc_now + india_offset
    india_time = india_now.time()
    
    print(f"🇮🇳 Current India time: {india_time.strftime('%I:%M %p')}")
    
    today = date.today()
    sent_count = 0
    
    # Find all students with preferences
    all_prefs = DailyDigestPreference.objects.filter(is_enabled=True)
    
    for pref in all_prefs:
        student = pref.student
        pref_time = pref.digest_time
        
        print(f"\n👤 {student.username}:")
        print(f"   Preference: {pref_time.strftime('%I:%M %p')}")
        print(f"   Should send: {india_time >= pref_time}")
        
        # Check if current India time is past their preference
        if india_time >= pref_time:
            # Find unsent digest
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=today,
                is_sent=False
            ).first()
            
            if digest:
                try:
                    from django.core.mail import send_mail
                    
                    print(f"   📤 Sending email...")
                    
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
                    
                    print(f"   ✅ Email sent to {student.email}")
                    sent_count += 1
                    
                except Exception as e:
                    print(f"   ❌ Failed to send: {e}")
            else:
                print(f"   📭 No unsent digest found")
        else:
            print(f"   ⏳ Not time yet")
    
    print(f"\n📊 Total emails sent: {sent_count}")
    return sent_count

if __name__ == "__main__":
    send_due_emails_india_time()
#!/usr/bin/env python3
"""
Send pending emails to students whose time has already passed
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
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def send_pending_emails():
    """Send emails to students whose time has passed"""
    
    print("📧 SENDING PENDING EMAILS")
    print("=" * 30)
    
    utc_now = timezone.now()
    india_offset = timedelta(hours=5, minutes=30)
    today = date.today()
    
    # Find students whose time has passed but haven't received emails
    students_to_send = []
    
    for pref in DailyDigestPreference.objects.filter(is_enabled=True):
        student = pref.student
        india_pref_time = pref.digest_time
        
        # Convert to UTC
        utc_equivalent_time = (
            datetime.combine(today, india_pref_time) - india_offset
        ).time()
        
        utc_equivalent_datetime = timezone.make_aware(
            datetime.combine(today, utc_equivalent_time)
        )
        
        # Check if time passed and email not sent
        if utc_now >= utc_equivalent_datetime:
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=today,
                is_sent=False
            ).first()
            
            if digest:
                students_to_send.append((student, digest, india_pref_time))
    
    print(f"📊 Students ready for email: {len(students_to_send)}")
    
    if students_to_send:
        print("\n👥 Students to receive emails:")
        for student, digest, india_time in students_to_send:
            print(f"   • {student.username} ({student.email}) - {india_time.strftime('%I:%M %p')}")
        
        print(f"\n🚀 Sending emails...")
        
        sent_count = 0
        
        for student, digest, india_time in students_to_send:
            try:
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
                
                sent_count += 1
                print(f"✅ Sent to {student.username} (India time: {india_time.strftime('%I:%M %p')})")
                
            except Exception as e:
                print(f"❌ Failed to send to {student.username}: {e}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total emails sent: {sent_count}")
        print(f"   Students notified: {sent_count}")
        
        if sent_count > 0:
            print(f"\n🎉 SUCCESS!")
            print("   Students should receive emails in their Gmail inboxes")
            print("   Digests will also appear in ClassWave notification bar")
    else:
        print("   📭 No students ready for email")
        print("   All students either:")
        print("     • Haven't reached their preferred time yet")
        print("     • Already received their emails")

if __name__ == "__main__":
    send_pending_emails()
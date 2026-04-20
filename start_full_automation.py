#!/usr/bin/env python
"""
Start fully automatic ClassWave digest service
This runs independently and sends emails at exact times without needing web server
"""

import os
import django
import time
from datetime import date, datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.models import Reminder
from reminders.tasks import create_daily_digest_for_student
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

def start_full_automation():
    print("🚀 STARTING FULLY AUTOMATIC CLASSWAVE SERVICE")
    print("=" * 60)
    print("✅ No web server needed")
    print("✅ Sends emails at exact scheduled times")
    print("✅ Respects student time preferences")
    print("✅ Runs 24/7 in background")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    last_check_date = None
    
    try:
        while True:
            now = datetime.now()
            today = date.today()
            
            print(f"⏰ {now.strftime('%Y-%m-%d %H:%M:%S')} - Checking for due emails...")
            
            # Generate digests for new day
            if last_check_date != today:
                print(f"📅 New day detected: {today}")
                generate_daily_digests(today)
                last_check_date = today
            
            # Send due emails
            send_due_emails()
            
            print("   💤 Sleeping for 5 minutes...")
            time.sleep(300)  # Check every 5 minutes
            
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
        print("✅ All scheduled emails will be sent when service restarts")

def generate_daily_digests(target_date):
    """Generate daily digests for all students"""
    print(f"📧 Generating daily digests for {target_date}...")
    
    students = User.objects.filter(user_type='student')
    generated_count = 0
    
    for student in students:
        # Check if digest already exists
        existing = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=target_date
        ).first()
        
        if not existing:
            digest = create_daily_digest_for_student(student.id, target_date)
            if digest:
                generated_count += 1
                print(f"   ✅ Generated for {student.username}")
    
    print(f"📊 Generated {generated_count} new digests")

def send_due_emails():
    """Send emails that are due now"""
    now = timezone.now()
    
    # Find due emails
    due_emails = Reminder.objects.filter(
        reminder_type='daily_digest',
        is_sent=False,
        reminder_time__lte=now
    )
    
    if due_emails.exists():
        print(f"📤 Found {due_emails.count()} due emails")
        
        sent_count = 0
        for email in due_emails:
            try:
                send_mail(
                    subject=f'📅 Your Schedule for {email.digest_date.strftime("%A, %B %d, %Y")}',
                    message=email.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email.student.email],
                    fail_silently=False,
                )
                
                email.is_sent = True
                email.sent_at = now
                email.save()
                
                print(f"   ✅ Sent to {email.student.username} ({email.student.email})")
                sent_count += 1
                
            except Exception as e:
                print(f"   ❌ Failed to send to {email.student.username}: {e}")
        
        print(f"📊 Successfully sent {sent_count} emails")
    else:
        print("   ℹ️ No due emails at this time")

if __name__ == "__main__":
    start_full_automation()
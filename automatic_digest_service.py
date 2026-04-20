#!/usr/bin/env python
"""
ClassWave Automatic Daily Digest Service
Runs in background and automatically generates/sends daily digests
"""

import os
import django
import time
from datetime import date, datetime, timedelta
import threading

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.models import Reminder
from reminders.tasks import create_daily_digest_for_student
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

class AutoDigestService:
    def __init__(self):
        self.running = True
        self.last_generation_date = None
        
    def start(self):
        print("🤖 ClassWave Automatic Digest Service Started")
        print("📅 Monitoring for daily digest generation and sending...")
        print("⏰ Checking every 5 minutes")
        print("🛑 Press Ctrl+C to stop")
        print()
        
        try:
            while self.running:
                self.check_and_process()
                time.sleep(300)  # Check every 5 minutes
        except KeyboardInterrupt:
            print("\n🛑 Service stopped by user")
        except Exception as e:
            print(f"\n❌ Service error: {e}")
    
    def check_and_process(self):
        """Check if digests need to be generated or sent"""
        today = date.today()
        
        # Generate digests for new day
        if self.last_generation_date != today:
            generated = self.generate_daily_digests(today)
            if generated > 0:
                print(f"✅ Generated {generated} digests for {today}")
            self.last_generation_date = today
        
        # Send due digests
        sent = self.send_due_digests()
        if sent > 0:
            print(f"📧 Sent {sent} digest emails")
    
    def generate_daily_digests(self, target_date):
        """Generate digests for all students for the target date"""
        students = User.objects.filter(user_type='student')
        generated_count = 0
        
        for student in students:
            # Check if digest already exists
            existing = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=target_date
            ).exists()
            
            if not existing:
                digest = create_daily_digest_for_student(student.id, target_date)
                if digest:
                    generated_count += 1
        
        return generated_count
    
    def send_due_digests(self):
        """Send digests that are due"""
        now = timezone.now()
        
        due_digests = Reminder.objects.filter(
            reminder_type='daily_digest',
            is_sent=False,
            reminder_time__lte=now
        )
        
        sent_count = 0
        for digest in due_digests:
            try:
                send_mail(
                    subject=f'📅 Your Schedule for {digest.digest_date.strftime("%A, %B %d, %Y")}',
                    message=digest.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[digest.student.email],
                    fail_silently=False,
                )
                
                digest.is_sent = True
                digest.sent_at = now
                digest.save()
                
                sent_count += 1
                
            except Exception as e:
                print(f"❌ Failed to send to {digest.student.email}: {e}")
        
        return sent_count

if __name__ == "__main__":
    service = AutoDigestService()
    service.start()
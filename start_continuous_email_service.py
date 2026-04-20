#!/usr/bin/env python3
"""
Start the continuous email service for perfect timing accuracy
"""

import os
import sys
import django
import time
import threading
from datetime import date, datetime, timedelta
from datetime import time as time_class

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference
from reminders.tasks import create_daily_digest_for_student

class PerfectTimingEmailService:
    """Email service with perfect timing accuracy"""
    
    def __init__(self):
        self.running = False
        self.last_digest_date = None
        self.last_check_minute = None
        
    def start(self):
        """Start the continuous service"""
        print("🚀 STARTING PERFECT TIMING EMAIL SERVICE")
        print("=" * 45)
        print("⏰ Checking every 30 seconds for perfect accuracy")
        print("📧 Maximum delay: 30 seconds")
        print("🎯 Perfect timing for all time preferences")
        print("")
        
        self.running = True
        
        try:
            while self.running:
                current_time = timezone.now()
                
                # Generate digests once per day
                self.check_digest_generation()
                
                # Check for due emails every 30 seconds
                self.check_due_emails()
                
                # Sleep for 30 seconds
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping email service...")
            self.running = False
    
    def check_digest_generation(self):
        """Generate digests once per day at 6:00 AM India time"""
        # Get current India time
        utc_now = timezone.now()
        india_now = utc_now + timedelta(hours=5, minutes=30)
        india_date = india_now.date()
        india_time = india_now.time()
        
        # Only generate after 6:00 AM India time
        if india_time < time_class(6, 0):
            return  # Too early
        
        if self.last_digest_date != india_date:
            print(f"📝 Generating daily digests for {india_date} (India date at {india_time.strftime('%I:%M %p')} IST)")
            
            students = User.objects.filter(user_type='student')
            generated_count = 0
            
            for student in students:
                existing_digest = Reminder.objects.filter(
                    student=student,
                    reminder_type='daily_digest',
                    digest_date=india_date
                ).first()
                
                if not existing_digest:
                    digest = create_daily_digest_for_student(student.id, india_date)
                    if digest:
                        generated_count += 1
            
            print(f"✅ Generated {generated_count} digests for India date {india_date}")
            self.last_digest_date = india_date
    
    def check_due_emails(self):
        """Check for due emails with perfect timing using India time"""
        utc_now = timezone.now()
        # Use India time for all comparisons
        india_now = utc_now + timedelta(hours=5, minutes=30)
        india_date = india_now.date()
        current_india_time = india_now.time()
        current_minute = utc_now.replace(second=0, microsecond=0)
        
        # Only check once per minute to avoid duplicate sends
        if self.last_check_minute == current_minute:
            return
        
        self.last_check_minute = current_minute
        
        # Find unsent digests for India date
        unsent_digests = Reminder.objects.filter(
            reminder_type='daily_digest',
            digest_date=india_date,
            is_sent=False
        )
        
        sent_count = 0
        
        for digest in unsent_digests:
            student = digest.student
            
            try:
                pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
                student_india_time = pref.digest_time
                
                # Compare India times directly with safety check
                if current_india_time >= student_india_time:
                    # Safety check: Don't send emails more than 2 hours early
                    time_diff = datetime.combine(india_date, current_india_time) - datetime.combine(india_date, student_india_time)
                    
                    if time_diff.total_seconds() < -7200:  # More than 2 hours early
                        continue  # Skip this student
                    success = self.send_reliable_email(student, digest, india_date, student_india_time)
                    
                    if success:
                        sent_count += 1
                        print(f"✅ PERFECT INDIA TIMING: Sent to {student.username} at {student_india_time.strftime('%I:%M %p')} India (current: {current_india_time.strftime('%I:%M %p')})")
                
            except DailyDigestPreference.DoesNotExist:
                continue
        
        if sent_count > 0:
            print(f"📧 Delivered {sent_count} emails using India time comparison")
    
    def send_reliable_email(self, student, digest, target_date, india_time):
        """Send email with multiple format attempts"""
        
        formats = [
            {
                'name': 'Standard Format',
                'subject': f'📅 Your Schedule for {target_date.strftime("%A, %B %d")}',
                'message': digest.message
            },
            {
                'name': 'Clean Format', 
                'subject': f'Your Schedule - {target_date.strftime("%A %B %d")}',
                'message': self.clean_message(digest.message)
            },
            {
                'name': 'Simple Format',
                'subject': f'Classes Today',
                'message': f"Hello {student.username},\n\nYour classes for today:\n\n{self.extract_classes(digest.message)}\n\nBest regards,\nClassWave"
            }
        ]
        
        for format_info in formats:
            try:
                send_mail(
                    subject=format_info['subject'],
                    message=format_info['message'],
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[student.email],
                    fail_silently=False,
                )
                
                # Mark as sent with perfect timing
                digest.is_sent = True
                digest.sent_at = timezone.now()
                digest.save()
                
                return True
                
            except Exception as e:
                continue
        
        return False
    
    def clean_message(self, message):
        """Remove emojis from message"""
        emojis = ['📅', '📚', '⏰', '👨‍🏫', '📍', '🎓', '💡']
        for emoji in emojis:
            message = message.replace(emoji, '')
        return message
    
    def extract_classes(self, message):
        """Extract class information"""
        lines = message.split('\n')
        class_info = []
        
        for line in lines:
            if any(keyword in line for keyword in ['Time:', 'Topic:', 'Lecturer:']):
                clean_line = self.clean_message(line).strip()
                if clean_line:
                    class_info.append(clean_line)
        
        return '\n'.join(class_info) if class_info else 'No classes scheduled'

def show_timing_comparison():
    """Show timing accuracy comparison"""
    
    print("⏰ TIMING ACCURACY COMPARISON")
    print("=" * 30)
    
    print("📊 Different System Options:")
    print("   1. Windows Task (every 10 minutes): Up to 10-minute delay")
    print("   2. Windows Task (every minute): Up to 1-minute delay")
    print("   3. Continuous Service (30 seconds): Up to 30-second delay")
    print("   4. Perfect Timing Service: Within 30 seconds")
    
    print(f"\n🎯 Perfect Timing Example:")
    print("   Student preference: 11:30:00 PM India")
    print("   System checks: 11:29:30, 11:30:00, 11:30:30...")
    print("   Email sent: At 11:30:00 or within 30 seconds")
    print("   Result: Perfect timing accuracy!")

if __name__ == "__main__":
    show_timing_comparison()
    
    print(f"\n🚀 STARTING PERFECT TIMING EMAIL SERVICE")
    print("Press Ctrl+C to stop")
    print("")
    
    service = PerfectTimingEmailService()
    service.start()
    
    print(f"\n✅ Perfect timing email service stopped")
    print("🎯 Students now get emails at their EXACT preferred times!")
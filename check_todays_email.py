#!/usr/bin/env python
"""
Check today's email content that was sent to students
"""

import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from reminders.models import Reminder

def check_todays_email():
    today = date.today()
    
    print("📧 TODAY'S DIGEST EMAIL CONTENT")
    print("=" * 60)
    print(f"📅 Date: {today}")
    
    digest = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today
    ).first()
    
    if digest:
        print(f"👤 Student: {digest.student.username}")
        print(f"📧 Email: {digest.student.email}")
        print(f"✅ Status: {'SENT' if digest.is_sent else 'PENDING'}")
        print(f"\n📝 EMAIL CONTENT:")
        print("-" * 40)
        print(digest.message)
        print("-" * 40)
        
        # Count schedules in the message
        schedule_count = digest.message.count('📚 Topic:')
        print(f"\n📊 Contains {schedule_count} classes for today")
        
    else:
        print("❌ No digest found for today")

if __name__ == "__main__":
    check_todays_email()
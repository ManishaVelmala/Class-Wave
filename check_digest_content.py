#!/usr/bin/env python
"""
Check what's in the current daily digest
"""

import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.models import Reminder

def check_digest_content():
    today = date.today()
    print(f"🗓️  CHECKING DIGEST CONTENT FOR: {today}")
    print("=" * 50)
    
    # Get a student
    student = User.objects.filter(user_type='student').first()
    print(f"👤 Checking digest for: {student.username}")
    
    # Get today's digest
    digest = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).first()
    
    if digest:
        print(f"\n📧 DIGEST MESSAGE:")
        print("=" * 50)
        print(digest.message)
        print("=" * 50)
        print(f"📅 Created: {digest.reminder_time}")
        print(f"📧 Sent: {digest.is_sent}")
        print(f"📖 Read: {digest.is_read}")
    else:
        print("❌ No digest found for today")

if __name__ == "__main__":
    check_digest_content()
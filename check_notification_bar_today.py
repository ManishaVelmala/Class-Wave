#!/usr/bin/env python
"""
Check what appears in the notification bar for students today
"""

import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.models import Reminder
from django.utils import timezone
from django.db.models import Q

def check_notification_bar_today():
    today = date.today()
    now = timezone.now()
    
    print(f"🗓️  CHECKING NOTIFICATION BAR FOR: {today}")
    print("=" * 50)
    
    students = User.objects.filter(user_type='student')
    
    for student in students:
        print(f"\n👤 {student.username} ({student.email})")
        
        # Use the same logic as the notification bar (from views.py)
        notifications = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest'
        ).filter(
            Q(reminder_time__lte=now) |  # Due digests
            Q(is_sent=True)  # OR digests sent via email
        ).order_by('-reminder_time')
        
        print(f"   📱 Total notifications: {notifications.count()}")
        
        # Show the most recent notifications
        for i, notif in enumerate(notifications[:3], 1):
            status = "📧 Sent" if notif.is_sent else "⏳ Pending"
            read_status = "📖 Read" if notif.is_read else "🔔 Unread"
            
            print(f"   {i}. {notif.digest_date} - {status} - {read_status}")
            
            # Show if this is today's digest
            if notif.digest_date == today:
                print(f"      ⭐ THIS IS TODAY'S DIGEST!")
        
        # Check specifically for today's digest
        todays_digest = notifications.filter(digest_date=today).first()
        if todays_digest:
            print(f"   ✅ Today's digest found!")
            print(f"      📅 Date: {todays_digest.digest_date}")
            print(f"      📧 Sent: {todays_digest.is_sent}")
            print(f"      📖 Read: {todays_digest.is_read}")
        else:
            print(f"   ❌ No digest found for today")

if __name__ == "__main__":
    check_notification_bar_today()
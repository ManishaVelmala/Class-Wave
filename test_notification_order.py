#!/usr/bin/env python
"""
Test the new notification ordering logic
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
from django.db.models import Q, Case, When, Value, IntegerField

def test_notification_order():
    today = date.today()
    now = timezone.now()
    
    print(f"🗓️  TESTING NEW NOTIFICATION ORDER FOR: {today}")
    print("=" * 50)
    
    # Get a student
    student = User.objects.filter(user_type='student').first()
    print(f"👤 Testing with student: {student.username}")
    
    # Use the NEW logic from views.py
    all_notifications = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest'
    ).filter(
        Q(reminder_time__lte=now) |
        Q(is_sent=True)
    ).annotate(
        is_today=Case(
            When(digest_date=today, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('-is_today', '-digest_date')
    
    print(f"\n📱 Notifications in NEW order:")
    for i, notif in enumerate(all_notifications, 1):
        is_today_marker = "⭐ TODAY" if notif.digest_date == today else ""
        status = "📧 Sent" if notif.is_sent else "⏳ Pending"
        read_status = "📖 Read" if notif.is_read else "🔔 Unread"
        
        print(f"   {i}. {notif.digest_date} - {status} - {read_status} {is_today_marker}")

if __name__ == "__main__":
    test_notification_order()
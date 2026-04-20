#!/usr/bin/env python
"""
Test the dual digest system:
1. Send digest to email inbox
2. Verify same digest appears in notification bar
"""

import os
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.models import Reminder
from reminders.tasks import create_daily_digest_for_student
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q

def test_dual_digest_system():
    print("🔄 TESTING DUAL DIGEST SYSTEM")
    print("=" * 50)
    print("1. Send digest to email inbox")
    print("2. Verify same digest appears in notification bar")
    print()
    
    # Test with a specific student
    student = User.objects.filter(user_type='student').first()
    if not student:
        print("❌ No students found!")
        return
    
    print(f"👤 Testing with: {student.username} ({student.email})")
    
    # Test date
    target_date = date(2025, 12, 11)
    print(f"📅 Target date: {target_date}")
    
    # Step 1: Create and send digest via email
    print(f"\n🔄 STEP 1: Creating and sending digest via email...")
    
    digest = create_daily_digest_for_student(student.id, target_date)
    if not digest:
        print("❌ No digest created (no classes on this date)")
        return
    
    print(f"✅ Digest created in database")
    print(f"   📝 Message preview: {digest.message[:100]}...")
    print(f"   ⏰ Scheduled time: {digest.reminder_time}")
    print(f"   📧 Sent status: {digest.is_sent}")
    
    # Send email
    try:
        send_mail(
            subject=f'📅 Your Schedule for {target_date.strftime("%A, %B %d, %Y")}',
            message=digest.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            fail_silently=False,
        )
        
        # Mark as sent (this is key for notification bar visibility)
        digest.is_sent = True
        digest.sent_at = timezone.now()
        digest.save()
        
        print(f"✅ Email sent to: {student.email}")
        print(f"✅ Digest marked as sent: {digest.is_sent}")
        
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return
    
    # Step 2: Check if digest appears in notification bar
    print(f"\n🔄 STEP 2: Checking notification bar visibility...")
    
    now = timezone.now()
    
    # Use the same logic as the views.py notifications function
    notifications = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest'
    ).filter(
        Q(reminder_time__lte=now) |  # Due digests
        Q(is_sent=True)  # OR digests that were sent via email
    ).order_by('-reminder_time')
    
    print(f"📊 Total notifications for {student.username}: {notifications.count()}")
    
    # Check if our digest is included
    our_digest = notifications.filter(id=digest.id).first()
    
    if our_digest:
        print(f"✅ SUCCESS: Digest appears in notification bar!")
        print(f"   📝 Digest ID: {our_digest.id}")
        print(f"   📅 Date: {our_digest.digest_date}")
        print(f"   📧 Sent: {our_digest.is_sent}")
        print(f"   📖 Read: {our_digest.is_read}")
    else:
        print(f"❌ FAILED: Digest does not appear in notification bar")
        
        # Debug info
        print(f"\n🔍 DEBUG INFO:")
        print(f"   Digest ID: {digest.id}")
        print(f"   Is sent: {digest.is_sent}")
        print(f"   Reminder time: {digest.reminder_time}")
        print(f"   Current time: {now}")
        print(f"   Time check: {digest.reminder_time <= now}")
    
    # Step 3: Show all notifications for this student
    print(f"\n📋 ALL NOTIFICATIONS FOR {student.username}:")
    for i, notif in enumerate(notifications[:5], 1):
        status = "📧 Sent" if notif.is_sent else "⏳ Pending"
        read_status = "📖 Read" if notif.is_read else "🔔 Unread"
        print(f"   {i}. {notif.digest_date} - {status} - {read_status}")
    
    if notifications.count() > 5:
        print(f"   ... and {notifications.count() - 5} more")
    
    return True

if __name__ == "__main__":
    test_dual_digest_system()
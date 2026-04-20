#!/usr/bin/env python3
"""
Fix the digest time for students who have 9:42 PM preference
"""

import os
import sys
import django
from datetime import date, time, datetime
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def fix_942pm_digest_time():
    """Fix digest times for students with 9:42 PM preference"""
    
    print("🔧 FIXING 9:42 PM DIGEST TIMES")
    print("=" * 40)
    
    # Find students with 9:42 PM preference
    target_time = time(21, 42)  # 9:42 PM
    students_942pm = DailyDigestPreference.objects.filter(
        digest_time=target_time,
        is_enabled=True
    )
    
    print(f"👥 Students with 9:42 PM preference: {students_942pm.count()}")
    
    today = date.today()
    fixed_count = 0
    
    for pref in students_942pm:
        student = pref.student
        print(f"\n👤 Fixing digest for: {student.username}")
        
        # Find today's digest
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if digest:
            old_time = digest.reminder_time
            
            # Calculate correct reminder time
            correct_datetime = datetime.combine(today, target_time)
            correct_datetime = timezone.make_aware(correct_datetime)
            
            print(f"   📅 Old reminder time: {old_time}")
            print(f"   📅 New reminder time: {correct_datetime}")
            
            # Update the digest
            digest.reminder_time = correct_datetime
            digest.is_sent = False  # Reset sent status
            digest.save()
            
            print(f"   ✅ Fixed digest time for {student.username}")
            fixed_count += 1
        else:
            print(f"   ❌ No digest found for {student.username}")
    
    print(f"\n📊 Fixed {fixed_count} digest times")
    
    # Now check if any digests are due to be sent
    now = timezone.now()
    due_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=False,
        reminder_time__lte=now
    )
    
    print(f"\n📧 Digests due to be sent now: {due_digests.count()}")
    
    for digest in due_digests:
        print(f"   📝 {digest.student.username}: {digest.reminder_time}")

def send_due_digests_now():
    """Send any digests that are due now"""
    
    print("\n📧 SENDING DUE DIGESTS")
    print("=" * 30)
    
    today = date.today()
    now = timezone.now()
    
    due_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=False,
        reminder_time__lte=now
    )
    
    if not due_digests.exists():
        print("📭 No digests due to be sent")
        return
    
    print(f"📧 Sending {due_digests.count()} due digests...")
    
    from django.core.mail import send_mail
    from django.conf import settings
    
    sent_count = 0
    
    for digest in due_digests:
        try:
            print(f"   📤 Sending to {digest.student.username}...")
            
            # Send email
            send_mail(
                subject=f'📅 Your Schedule for {digest.digest_date.strftime("%A, %B %d, %Y")}',
                message=digest.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[digest.student.email],
                fail_silently=False,
            )
            
            # Mark as sent
            digest.is_sent = True
            digest.sent_at = now
            digest.save()
            
            print(f"   ✅ Email sent to {digest.student.email}")
            sent_count += 1
            
        except Exception as e:
            print(f"   ❌ Failed to send to {digest.student.email}: {e}")
    
    print(f"\n📊 Successfully sent {sent_count} emails")

if __name__ == "__main__":
    fix_942pm_digest_time()
    
    # Ask if user wants to send due digests
    response = input("\n🤔 Do you want to send due digests now? (y/n): ")
    if response.lower() == 'y':
        send_due_digests_now()
    
    print("\n✅ DIGEST TIME FIX COMPLETE!")
    print("📋 The system will now correctly use student time preferences.")
    print("   No more subtracting days for evening times!")
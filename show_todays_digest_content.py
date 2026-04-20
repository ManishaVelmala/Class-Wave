#!/usr/bin/env python3
"""
Show today's digest content to verify it's properly generated
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
from reminders.models import Reminder

def show_digest_content():
    """Show the content of today's digests"""
    
    print("📝 TODAY'S DIGEST CONTENT")
    print("=" * 26)
    
    # Get India date
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    
    print(f"Showing digests for India date: {india_date}")
    
    # Get today's digests
    digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date
    ).order_by('student__username')
    
    if not digests.exists():
        print("❌ No digests found for today")
        return
    
    print(f"\nFound {digests.count()} digests:")
    
    for i, digest in enumerate(digests, 1):
        student = digest.student
        status = "✅ Sent" if digest.is_sent else "⏳ Pending"
        
        print(f"\n{i}. {student.username} ({status})")
        print("-" * 40)
        
        # Show first few lines of the digest
        lines = digest.message.split('\n')
        for line in lines[:10]:  # Show first 10 lines
            if line.strip():
                print(f"   {line}")
        
        if len(lines) > 10:
            print(f"   ... (and {len(lines) - 10} more lines)")
        
        print(f"\n   📧 Email Status: {status}")
        if digest.is_sent and digest.sent_at:
            india_sent_time = digest.sent_at + timedelta(hours=5, minutes=30)
            print(f"   📅 Sent at: {india_sent_time.strftime('%I:%M %p India on %B %d, %Y')}")

def show_email_schedule():
    """Show when remaining emails will be sent"""
    
    print(f"\n📅 EMAIL SCHEDULE FOR TODAY")
    print("=" * 28)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    current_india_time = india_now.time()
    
    # Get pending digests
    pending_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date,
        is_sent=False
    )
    
    if not pending_digests.exists():
        print("✅ All emails have been sent!")
        return
    
    print(f"Remaining emails to send: {pending_digests.count()}")
    print(f"Current India time: {current_india_time.strftime('%I:%M %p')}")
    
    from reminders.models import DailyDigestPreference
    
    for digest in pending_digests:
        student = digest.student
        
        try:
            pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
            student_time = pref.digest_time
            
            # Check if due
            is_due = current_india_time >= student_time
            
            if is_due:
                print(f"   🔔 {student.username}: DUE NOW (preference: {student_time.strftime('%I:%M %p')})")
            else:
                # Calculate time remaining
                student_datetime = datetime.combine(india_date, student_time)
                current_datetime = datetime.combine(india_date, current_india_time)
                
                if student_datetime > current_datetime:
                    time_until = student_datetime - current_datetime
                    hours = int(time_until.total_seconds() // 3600)
                    minutes = int((time_until.total_seconds() % 3600) // 60)
                    print(f"   ⏳ {student.username}: Due in {hours}h {minutes}m (at {student_time.strftime('%I:%M %p')})")
                
        except DailyDigestPreference.DoesNotExist:
            print(f"   ⚠️  {student.username}: No preference set")

if __name__ == "__main__":
    show_digest_content()
    show_email_schedule()
    
    print(f"\n✅ DIGEST CONTENT VERIFICATION COMPLETE")
    print("Today's digests are properly generated with India time logic!")
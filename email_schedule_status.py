#!/usr/bin/env python3
"""
Show email schedule status and when emails will be sent
"""

import os
import sys
import django
from datetime import date, time, datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def show_email_schedule():
    """Show when emails will be sent"""
    
    print("📅 EMAIL SCHEDULE STATUS")
    print("=" * 35)
    
    now = timezone.now()
    current_time = now.time()
    today = date.today()
    
    print(f"🕐 Current time (India): {current_time.strftime('%I:%M %p')}")
    print(f"📅 Date: {today}")
    print(f"🌍 Timezone: {now.tzinfo}")
    
    print(f"\n📧 EMAIL SCHEDULE FOR TODAY:")
    print("-" * 40)
    
    all_prefs = DailyDigestPreference.objects.filter(is_enabled=True).order_by('digest_time')
    
    for pref in all_prefs:
        student = pref.student
        pref_time = pref.digest_time
        
        # Check digest status
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        # Calculate time until email
        if current_time < pref_time:
            time_diff = datetime.combine(today, pref_time) - datetime.combine(today, current_time)
            hours = int(time_diff.total_seconds() // 3600)
            minutes = int((time_diff.total_seconds() % 3600) // 60)
            time_until = f"in {hours}h {minutes}m"
        else:
            time_until = "NOW"
        
        # Status
        if digest:
            if digest.is_sent:
                status = "✅ SENT"
                detail = f"at {digest.sent_at.strftime('%I:%M %p')}"
            elif current_time >= pref_time:
                status = "📤 DUE NOW"
                detail = "ready to send"
            else:
                status = "⏳ PENDING"
                detail = time_until
        else:
            status = "❌ NO DIGEST"
            detail = "no classes today"
        
        print(f"   {pref_time.strftime('%I:%M %p')} - {student.username}")
        print(f"      Status: {status} ({detail})")
    
    # Show next email
    print(f"\n🔮 NEXT EMAIL TO BE SENT:")
    
    next_student = None
    next_time = None
    next_time_until = None
    
    for pref in all_prefs:
        if current_time < pref.digest_time:
            digest = Reminder.objects.filter(
                student=pref.student,
                reminder_type='daily_digest',
                digest_date=today,
                is_sent=False
            ).first()
            
            if digest:
                next_student = pref.student.username
                next_time = pref.digest_time
                
                time_diff = datetime.combine(today, pref.digest_time) - datetime.combine(today, current_time)
                hours = int(time_diff.total_seconds() // 3600)
                minutes = int((time_diff.total_seconds() % 3600) // 60)
                next_time_until = f"{hours}h {minutes}m"
                break
    
    if next_student:
        print(f"   👤 Student: {next_student}")
        print(f"   ⏰ Time: {next_time.strftime('%I:%M %p')}")
        print(f"   ⏳ In: {next_time_until}")
        print(f"   📧 Email will be sent automatically!")
    else:
        print(f"   📭 No more emails scheduled for today")

def test_manual_send():
    """Test sending email manually for testing"""
    
    print(f"\n🧪 MANUAL EMAIL TEST")
    print("=" * 25)
    
    # Find students with unsent digests
    today = date.today()
    unsent_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=False
    )
    
    print(f"📝 Students with unsent digests: {unsent_digests.count()}")
    
    for digest in unsent_digests:
        student = digest.student
        
        # Get their preference
        try:
            pref = DailyDigestPreference.objects.get(student=student)
            pref_time = pref.digest_time
            
            print(f"\n👤 {student.username}:")
            print(f"   Preference: {pref_time.strftime('%I:%M %p')}")
            print(f"   Email: {student.email}")
            
            # Ask if user wants to send now for testing
            response = input(f"   🤔 Send test email now? (y/n): ")
            if response.lower() == 'y':
                try:
                    from django.core.mail import send_mail
                    from django.conf import settings
                    
                    send_mail(
                        subject=f'📅 Your Schedule for {today.strftime("%A, %B %d, %Y")}',
                        message=digest.message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[student.email],
                        fail_silently=False,
                    )
                    
                    # Mark as sent
                    digest.is_sent = True
                    digest.sent_at = timezone.now()
                    digest.save()
                    
                    print(f"   ✅ Test email sent to {student.email}!")
                    
                except Exception as e:
                    print(f"   ❌ Failed to send: {e}")
            
        except DailyDigestPreference.DoesNotExist:
            print(f"\n👤 {student.username}: No preference set")

if __name__ == "__main__":
    show_email_schedule()
    
    print(f"\n" + "=" * 50)
    print("🎯 HOW THE SYSTEM WORKS:")
    print("   1. Student sets preference (e.g., 10:18 PM)")
    print("   2. System waits until that exact time")
    print("   3. Email is sent automatically")
    print("   4. Student receives email at preferred time")
    
    print(f"\n🚀 TO START AUTOMATIC MONITORING:")
    print("   Run: python start_email_monitoring.py")
    print("   This will send emails at the exact times!")
    
    response = input(f"\n🤔 Do you want to test manual sending? (y/n): ")
    if response.lower() == 'y':
        test_manual_send()
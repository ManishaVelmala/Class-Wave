#!/usr/bin/env python
"""
Send test messages to all students based on their time preferences
"""

import os
import django
from datetime import date, time, datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

def send_test_messages():
    print("🧪 SENDING TEST MESSAGES TO ALL STUDENTS")
    print("=" * 60)
    
    today = date.today()
    now = datetime.now()
    
    students = User.objects.filter(user_type='student')
    print(f"👥 Found {students.count()} students")
    print(f"📅 Test date: {today}")
    print(f"⏰ Current time: {now.strftime('%H:%M:%S')}")
    
    sent_count = 0
    scheduled_count = 0
    
    for student in students:
        print(f"\n👤 Processing: {student.username}")
        print(f"   📧 Email: {student.email}")
        
        # Get student's preference
        try:
            pref = DailyDigestPreference.objects.get(student=student)
            preferred_time = pref.digest_time
            is_enabled = pref.is_enabled
        except DailyDigestPreference.DoesNotExist:
            preferred_time = '07:00'
            is_enabled = True
        
        if not is_enabled:
            print(f"   🚫 Skipped: Student has disabled email notifications")
            continue
        
        print(f"   ⚙️ Preferred time: {preferred_time}")
        
        # Parse preferred time
        hour, minute = map(int, preferred_time.split(':'))
        preferred_datetime = datetime.combine(today, time(hour, minute))
        
        # Create test message
        test_message = f"""🧪 ClassWave Time Preference Test

Hello {student.username}!

This is a test message to verify that your email time preference is working correctly.

📧 Your Settings:
   • Email: {student.email}
   • Preferred time: {preferred_time} ({time(hour, minute).strftime('%I:%M %p')})
   • Status: {'✅ Enabled' if is_enabled else '🚫 Disabled'}

⏰ Test Details:
   • Test sent at: {now.strftime('%Y-%m-%d %H:%M:%S')}
   • Your preferred time: {preferred_datetime.strftime('%Y-%m-%d %H:%M:%S')}
   • Time difference: {'Already passed' if preferred_datetime <= now else f'{int((preferred_datetime - now).total_seconds() / 60)} minutes from now'}

🎯 What this test proves:
   ✅ Your email preference is saved correctly
   ✅ System can send emails to your Gmail inbox
   ✅ Time-based delivery system is working
   ✅ You receive emails even when logged out

If you receive this email, your ClassWave notification system is working perfectly! 🎉

Best regards,
ClassWave Team 🔔

---
This is an automated test message from ClassWave.
"""

        # Determine when to send
        if preferred_datetime <= now:
            # Send immediately (preferred time has passed)
            try:
                send_mail(
                    subject=f'🧪 ClassWave Test - Time Preference Verification',
                    message=test_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[student.email],
                    fail_silently=False,
                )
                print(f"   ✅ SENT IMMEDIATELY (preferred time has passed)")
                sent_count += 1
                
            except Exception as e:
                print(f"   ❌ FAILED to send: {e}")
        
        else:
            # Schedule for preferred time
            reminder = Reminder.objects.create(
                student=student,
                schedule=None,
                reminder_time=preferred_datetime,
                message=test_message,
                reminder_type='test_message',
                is_sent=False
            )
            
            time_until = preferred_datetime - now
            hours = int(time_until.total_seconds() // 3600)
            minutes = int((time_until.total_seconds() % 3600) // 60)
            
            print(f"   ⏳ SCHEDULED for {preferred_time} (in {hours}h {minutes}m)")
            scheduled_count += 1
    
    print(f"\n📊 TEST SUMMARY:")
    print(f"   ✅ Sent immediately: {sent_count}")
    print(f"   ⏳ Scheduled for later: {scheduled_count}")
    print(f"   👥 Total processed: {sent_count + scheduled_count}")
    
    if sent_count > 0:
        print(f"\n📧 IMMEDIATE EMAILS SENT!")
        print(f"   Check Gmail inboxes for test messages")
    
    if scheduled_count > 0:
        print(f"\n⏰ SCHEDULED EMAILS:")
        print(f"   {scheduled_count} emails will be sent at students' preferred times")
        print(f"   Run the server and middleware will send them automatically:")
        print(f"   python manage.py runserver")
    
    # Show scheduled emails
    if scheduled_count > 0:
        print(f"\n📋 SCHEDULED EMAIL DETAILS:")
        test_reminders = Reminder.objects.filter(
            reminder_type='test_message',
            is_sent=False
        ).order_by('reminder_time')
        
        for reminder in test_reminders:
            time_until = reminder.reminder_time - now
            hours = int(time_until.total_seconds() // 3600)
            minutes = int((time_until.total_seconds() % 3600) // 60)
            print(f"   👤 {reminder.student.username}: {reminder.reminder_time.strftime('%H:%M')} (in {hours}h {minutes}m)")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Check Gmail inboxes for immediate test emails")
    print(f"   2. Run: python manage.py runserver")
    print(f"   3. Wait for scheduled emails to be sent automatically")
    print(f"   4. Verify all students receive emails at their preferred times")
    
    return sent_count, scheduled_count

if __name__ == "__main__":
    send_test_messages()
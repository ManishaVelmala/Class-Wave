#!/usr/bin/env python
"""
Diagnose why today's schedule emails are not being sent to students
"""

import os
import django
from datetime import date, datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from schedules.models import Schedule
from reminders.models import Reminder, DailyDigestPreference
from django.conf import settings
from django.utils import timezone

def diagnose_email_issue():
    today = date.today()
    now = datetime.now()
    
    print("🔍 DIAGNOSING EMAIL DELIVERY ISSUE")
    print("=" * 60)
    print(f"📅 Today's date: {today}")
    print(f"⏰ Current time: {now.strftime('%H:%M:%S')}")
    print()
    
    # Step 1: Check if there are schedules for today
    print("1️⃣ CHECKING SCHEDULES FOR TODAY:")
    todays_schedules = Schedule.objects.filter(date=today)
    print(f"   📚 Schedules for {today}: {todays_schedules.count()}")
    
    if todays_schedules.exists():
        for schedule in todays_schedules:
            print(f"   • {schedule.subject_name} ({schedule.start_time} - {schedule.end_time})")
            print(f"     Students assigned: {schedule.students.count()}")
    else:
        print("   ❌ NO SCHEDULES FOR TODAY - This is why no emails are sent!")
        print("   💡 Solution: Create schedules for today first")
        return
    
    # Step 2: Check students
    print(f"\n2️⃣ CHECKING STUDENTS:")
    students = User.objects.filter(user_type='student')
    print(f"   👥 Total students: {students.count()}")
    
    for student in students:
        print(f"   👤 {student.username} ({student.email})")
    
    # Step 3: Check email configuration
    print(f"\n3️⃣ CHECKING EMAIL CONFIGURATION:")
    print(f"   Backend: {settings.EMAIL_BACKEND}")
    print(f"   Host: {settings.EMAIL_HOST}")
    print(f"   User: {settings.EMAIL_HOST_USER}")
    print(f"   Password length: {len(settings.EMAIL_HOST_PASSWORD)} chars")
    
    # Step 4: Check existing digests for today
    print(f"\n4️⃣ CHECKING EXISTING DIGESTS:")
    todays_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today
    )
    
    print(f"   📧 Digests for {today}: {todays_digests.count()}")
    
    if todays_digests.exists():
        for digest in todays_digests:
            status = "✅ SENT" if digest.is_sent else "⏳ PENDING"
            print(f"   👤 {digest.student.username}: {status}")
            if digest.is_sent:
                print(f"      📅 Sent at: {digest.sent_at}")
            else:
                print(f"      ⏰ Scheduled for: {digest.reminder_time}")
    else:
        print("   ❌ NO DIGESTS CREATED FOR TODAY")
        print("   💡 Need to generate digests first")
    
    # Step 5: Check student preferences
    print(f"\n5️⃣ CHECKING STUDENT PREFERENCES:")
    for student in students:
        try:
            pref = DailyDigestPreference.objects.get(student=student)
            print(f"   👤 {student.username}: {pref.digest_time} ({'✅ Enabled' if pref.is_enabled else '🚫 Disabled'})")
        except DailyDigestPreference.DoesNotExist:
            print(f"   👤 {student.username}: 07:00 (Default)")
    
    # Step 6: Test Gmail connection
    print(f"\n6️⃣ TESTING GMAIL CONNECTION:")
    try:
        from django.core.mail import send_mail
        
        # Don't actually send, just test connection
        print("   🧪 Testing SMTP connection...")
        
        # This will test the connection without sending
        from django.core.mail import get_connection
        connection = get_connection()
        connection.open()
        connection.close()
        
        print("   ✅ Gmail SMTP connection: WORKING")
        
    except Exception as e:
        print(f"   ❌ Gmail SMTP connection: FAILED")
        print(f"   🔧 Error: {e}")
        print("   💡 Need to fix Gmail authentication")
    
    # Step 7: Provide diagnosis
    print(f"\n🎯 DIAGNOSIS:")
    
    if not todays_schedules.exists():
        print("   ❌ ROOT CAUSE: No schedules exist for today")
        print("   💡 SOLUTION: Create schedules for today first")
        
    elif not todays_digests.exists():
        print("   ❌ ROOT CAUSE: No digests have been generated")
        print("   💡 SOLUTION: Run digest generation command")
        
    elif todays_digests.filter(is_sent=False).exists():
        print("   ❌ ROOT CAUSE: Digests created but not sent")
        print("   💡 SOLUTION: Check time preferences and send due emails")
        
    else:
        print("   ✅ Digests appear to be sent - check Gmail inboxes")
    
    print(f"\n🚀 RECOMMENDED ACTIONS:")
    print("   1. Create schedules for today (if missing)")
    print("   2. Generate digests: python manage.py refresh_todays_digests")
    print("   3. Send emails: python manage.py send_due_emails")
    print("   4. Or run full automation: python start_full_automation.py")

if __name__ == "__main__":
    diagnose_email_issue()
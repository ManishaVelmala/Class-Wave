#!/usr/bin/env python3
"""
Diagnostic script to check why emails are not being sent at 9:42 PM
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
from reminders.tasks import create_daily_digest_for_student

def diagnose_942pm_issue():
    """Diagnose why emails aren't being sent at 9:42 PM"""
    
    print("🔍 DIAGNOSING 9:42 PM EMAIL ISSUE")
    print("=" * 50)
    
    # Find students with 9:42 PM preference
    target_time = time(21, 42)  # 9:42 PM
    students_942pm = DailyDigestPreference.objects.filter(
        digest_time=target_time,
        is_enabled=True
    )
    
    print(f"👥 Students with 9:42 PM preference: {students_942pm.count()}")
    
    if not students_942pm.exists():
        print("❌ No students found with 9:42 PM preference")
        
        # Check all student preferences
        all_prefs = DailyDigestPreference.objects.all()
        print(f"\n📊 All student preferences ({all_prefs.count()}):")
        for pref in all_prefs:
            print(f"   {pref.student.username}: {pref.digest_time.strftime('%I:%M %p')} (Enabled: {pref.is_enabled})")
        return
    
    today = date.today()
    now = timezone.now()
    current_time = now.time()
    
    print(f"📅 Today: {today}")
    print(f"🕐 Current time: {current_time.strftime('%I:%M %p')}")
    print(f"⏰ Target time: {target_time.strftime('%I:%M %p')}")
    
    for pref in students_942pm:
        student = pref.student
        print(f"\n👤 Checking student: {student.username} ({student.email})")
        print(f"   Preference: {pref.digest_time.strftime('%I:%M %p')}")
        print(f"   Enabled: {pref.is_enabled}")
        
        # Check if digest exists for today
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if digest:
            print(f"   📝 Digest exists: YES (ID: {digest.id})")
            print(f"      Created: {digest.created_at}")
            print(f"      Reminder time: {digest.reminder_time}")
            print(f"      Is sent: {digest.is_sent}")
            
            if digest.sent_at:
                print(f"      Sent at: {digest.sent_at}")
            
            # Check if digest should be sent now
            if digest.reminder_time:
                should_send = digest.reminder_time <= now
                print(f"      Should send now: {should_send}")
                
                if should_send and not digest.is_sent:
                    print("      ⚠️  ISSUE: Digest is due but not sent!")
                elif digest.is_sent:
                    print("      ✅ Digest already sent")
                else:
                    time_until = digest.reminder_time - now
                    print(f"      ⏳ Time until sending: {time_until}")
            else:
                print("      ❌ No reminder time set!")
        else:
            print("   📝 Digest exists: NO")
            
            # Try to create digest
            print("   🔧 Attempting to create digest...")
            try:
                new_digest = create_daily_digest_for_student(student.id, today)
                if new_digest:
                    print(f"      ✅ Digest created: ID {new_digest.id}")
                    print(f"      Reminder time: {new_digest.reminder_time}")
                else:
                    print("      ❌ No digest created (no classes today)")
            except Exception as e:
                print(f"      ❌ Error creating digest: {e}")

def check_background_service_status():
    """Check if background service is working"""
    
    print("\n🤖 CHECKING BACKGROUND SERVICE STATUS")
    print("=" * 45)
    
    today = date.today()
    now = timezone.now()
    
    # Find all due digests
    due_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=False,
        reminder_time__lte=now
    )
    
    print(f"📧 Due digests (should be sent): {due_digests.count()}")
    
    for digest in due_digests:
        print(f"   📝 Digest {digest.id}:")
        print(f"      Student: {digest.student.username}")
        print(f"      Scheduled: {digest.reminder_time}")
        print(f"      Overdue by: {now - digest.reminder_time}")
    
    # Check sent digests today
    sent_today = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True
    )
    
    print(f"\n📧 Sent digests today: {sent_today.count()}")
    
    for digest in sent_today:
        print(f"   📧 Sent to {digest.student.username} at {digest.sent_at}")

def check_task_scheduler_setup():
    """Check if Windows Task Scheduler is set up correctly"""
    
    print("\n⏰ CHECKING TASK SCHEDULER SETUP")
    print("=" * 40)
    
    # Check if the background service command exists
    import os
    
    command_file = "reminders/management/commands/send_real_daily_digests.py"
    if os.path.exists(command_file):
        print(f"✅ Background service command exists: {command_file}")
    else:
        print(f"❌ Background service command missing: {command_file}")
    
    # Check batch files
    batch_files = [
        "start_automatic_digests.bat",
        "daily_digest_automation.bat",
        "setup_daily_automation.bat"
    ]
    
    for batch_file in batch_files:
        if os.path.exists(batch_file):
            print(f"✅ Batch file exists: {batch_file}")
        else:
            print(f"❌ Batch file missing: {batch_file}")
    
    print("\n📋 TASK SCHEDULER REQUIREMENTS:")
    print("   1. Task should run daily at 6:00 AM")
    print("   2. Task should execute: python manage.py send_real_daily_digests")
    print("   3. Task should run even when user is not logged in")
    print("   4. Task should have highest privileges")

def manual_email_test():
    """Test sending emails manually for 9:42 PM students"""
    
    print("\n🧪 MANUAL EMAIL TEST")
    print("=" * 25)
    
    target_time = time(21, 42)  # 9:42 PM
    students_942pm = DailyDigestPreference.objects.filter(
        digest_time=target_time,
        is_enabled=True
    )
    
    if not students_942pm.exists():
        print("❌ No students with 9:42 PM preference to test")
        return
    
    today = date.today()
    now = timezone.now()
    
    for pref in students_942pm:
        student = pref.student
        print(f"\n👤 Testing manual email for: {student.username}")
        
        # Find or create digest
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if not digest:
            digest = create_daily_digest_for_student(student.id, today)
        
        if digest and not digest.is_sent:
            print("   📧 Attempting to send email manually...")
            
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                
                # Send email
                send_mail(
                    subject=f'📅 Your Schedule for {today.strftime("%A, %B %d, %Y")}',
                    message=digest.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[student.email],
                    fail_silently=False,
                )
                
                # Mark as sent
                digest.is_sent = True
                digest.sent_at = now
                digest.save()
                
                print(f"   ✅ Email sent successfully to {student.email}")
                
            except Exception as e:
                print(f"   ❌ Email sending failed: {e}")
        else:
            if digest and digest.is_sent:
                print("   ℹ️  Email already sent")
            else:
                print("   ❌ No digest available")

if __name__ == "__main__":
    diagnose_942pm_issue()
    check_background_service_status()
    check_task_scheduler_setup()
    
    # Ask if user wants to test manual sending
    print("\n" + "=" * 50)
    response = input("🤔 Do you want to test manual email sending? (y/n): ")
    if response.lower() == 'y':
        manual_email_test()
    
    print("\n📋 POSSIBLE SOLUTIONS:")
    print("   1. Check Windows Task Scheduler is running")
    print("   2. Verify task runs: python manage.py send_real_daily_digests")
    print("   3. Check Gmail SMTP settings are correct")
    print("   4. Ensure student has classes scheduled for today")
    print("   5. Verify time zone settings are correct")
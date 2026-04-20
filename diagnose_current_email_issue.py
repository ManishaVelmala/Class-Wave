#!/usr/bin/env python3
"""
Comprehensive diagnostic for current email sending issue
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

def diagnose_current_issue():
    """Diagnose the current email sending issue"""
    
    print("🔍 COMPREHENSIVE EMAIL DIAGNOSTIC")
    print("=" * 50)
    
    # Get current time info
    now = timezone.now()
    today = date.today()
    current_time = now.time()
    
    print(f"📅 Today: {today}")
    print(f"🕐 Current time: {current_time.strftime('%I:%M %p')}")
    print(f"🌍 Timezone: {now.tzinfo}")
    
    # Check all student preferences
    print(f"\n👥 ALL STUDENT PREFERENCES:")
    all_prefs = DailyDigestPreference.objects.all().order_by('digest_time')
    
    for pref in all_prefs:
        status = "✅ Enabled" if pref.is_enabled else "❌ Disabled"
        print(f"   {pref.student.username}: {pref.digest_time.strftime('%I:%M %p')} ({status})")
    
    # Check all digests for today
    print(f"\n📝 ALL DIGESTS FOR TODAY:")
    all_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today
    ).order_by('reminder_time')
    
    for digest in all_digests:
        is_due = digest.reminder_time <= now
        time_diff = digest.reminder_time - now
        
        print(f"   📧 {digest.student.username}:")
        print(f"      Scheduled: {digest.reminder_time}")
        print(f"      Is due: {is_due}")
        print(f"      Is sent: {digest.is_sent}")
        
        if is_due and not digest.is_sent:
            print(f"      ⚠️  OVERDUE by: {now - digest.reminder_time}")
        elif not is_due:
            print(f"      ⏳ Due in: {time_diff}")
        
        if digest.sent_at:
            print(f"      Sent at: {digest.sent_at}")
    
    # Find students with evening preferences who haven't received emails
    evening_students = []
    for pref in all_prefs:
        if pref.is_enabled and pref.digest_time.hour >= 20:  # 8 PM or later
            digest = Reminder.objects.filter(
                student=pref.student,
                reminder_type='daily_digest',
                digest_date=today
            ).first()
            
            if digest and not digest.is_sent:
                evening_students.append((pref.student, pref.digest_time, digest))
    
    if evening_students:
        print(f"\n🌙 EVENING STUDENTS WITH UNSENT EMAILS:")
        for student, pref_time, digest in evening_students:
            print(f"   👤 {student.username}:")
            print(f"      Preference: {pref_time.strftime('%I:%M %p')}")
            print(f"      Digest scheduled: {digest.reminder_time}")
            print(f"      Should send now: {digest.reminder_time <= now}")

def check_background_service():
    """Check if background service is working properly"""
    
    print(f"\n🤖 BACKGROUND SERVICE CHECK")
    print("=" * 35)
    
    # Check if the management command exists and works
    try:
        from reminders.management.commands.send_real_daily_digests import Command
        print("✅ Background service command exists")
        
        # Try to run it manually
        print("\n📤 Testing background service manually...")
        
        today = date.today()
        now = timezone.now()
        
        # Find due digests
        due_digests = Reminder.objects.filter(
            reminder_type='daily_digest',
            digest_date=today,
            is_sent=False,
            reminder_time__lte=now
        )
        
        print(f"📧 Due digests found: {due_digests.count()}")
        
        if due_digests.exists():
            print("🔧 Attempting to send due emails...")
            
            from django.core.mail import send_mail
            from django.conf import settings
            
            sent_count = 0
            
            for digest in due_digests:
                try:
                    print(f"   📤 Sending to {digest.student.username}...")
                    
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
        else:
            print("📭 No due emails to send")
            
    except ImportError as e:
        print(f"❌ Background service command not found: {e}")

def check_windows_task_scheduler():
    """Check Windows Task Scheduler status"""
    
    print(f"\n⏰ WINDOWS TASK SCHEDULER CHECK")
    print("=" * 40)
    
    print("📋 Task Scheduler Requirements:")
    print("   1. Task should run every few minutes or hourly")
    print("   2. Command: python manage.py send_real_daily_digests")
    print("   3. Working directory: Current project folder")
    print("   4. Run with highest privileges")
    print("   5. Run whether user is logged on or not")
    
    # Check if batch files exist
    batch_files = [
        "start_automatic_digests.bat",
        "daily_digest_automation.bat", 
        "setup_daily_automation.bat"
    ]
    
    print(f"\n📁 Batch Files Status:")
    for batch_file in batch_files:
        if os.path.exists(batch_file):
            print(f"   ✅ {batch_file}")
        else:
            print(f"   ❌ {batch_file} (missing)")

def test_email_sending():
    """Test email sending functionality"""
    
    print(f"\n📧 EMAIL SENDING TEST")
    print("=" * 30)
    
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        print("📤 Testing Gmail SMTP connection...")
        
        # Get a test student
        student = User.objects.filter(user_type='student').first()
        if not student:
            print("❌ No student found for testing")
            return
        
        print(f"👤 Testing with: {student.email}")
        
        # Test email
        send_mail(
            subject='🧪 ClassWave Email Test',
            message='This is a test email to verify Gmail SMTP is working correctly.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            fail_silently=False,
        )
        
        print(f"✅ Test email sent successfully to {student.email}")
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        print("🔧 Check Gmail SMTP settings in settings.py")

def check_digest_creation():
    """Check if digests are being created correctly"""
    
    print(f"\n📝 DIGEST CREATION CHECK")
    print("=" * 35)
    
    today = date.today()
    
    # Get students with evening preferences
    evening_prefs = DailyDigestPreference.objects.filter(
        digest_time__hour__gte=20,  # 8 PM or later
        is_enabled=True
    )
    
    print(f"🌙 Students with evening preferences: {evening_prefs.count()}")
    
    for pref in evening_prefs:
        student = pref.student
        print(f"\n👤 Checking {student.username}:")
        print(f"   Preference: {pref.digest_time.strftime('%I:%M %p')}")
        
        # Check if digest exists
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if digest:
            print(f"   📝 Digest exists: YES")
            print(f"      Scheduled for: {digest.reminder_time}")
            print(f"      Created at: {digest.created_at}")
        else:
            print(f"   📝 Digest exists: NO")
            
            # Try to create digest
            print(f"   🔧 Attempting to create digest...")
            try:
                new_digest = create_daily_digest_for_student(student.id, today)
                if new_digest:
                    print(f"      ✅ Digest created: {new_digest.reminder_time}")
                else:
                    print(f"      ❌ No digest created (no classes today)")
            except Exception as e:
                print(f"      ❌ Error creating digest: {e}")

if __name__ == "__main__":
    diagnose_current_issue()
    
    print("\n" + "=" * 50)
    response = input("🤔 Do you want to check background service? (y/n): ")
    if response.lower() == 'y':
        check_background_service()
    
    print("\n" + "=" * 50)
    response = input("🤔 Do you want to test email sending? (y/n): ")
    if response.lower() == 'y':
        test_email_sending()
    
    check_windows_task_scheduler()
    check_digest_creation()
    
    print("\n" + "=" * 50)
    print("🎯 POSSIBLE SOLUTIONS:")
    print("   1. Ensure Windows Task Scheduler is running the background service")
    print("   2. Check Gmail SMTP settings are correct")
    print("   3. Verify student has classes scheduled for today")
    print("   4. Run background service manually: python manage.py send_real_daily_digests")
    print("   5. Check system time zone settings")
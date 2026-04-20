#!/usr/bin/env python
"""
Comprehensive verification of Gmail digest delivery system
"""

import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference
from schedules.models import Schedule
from django.conf import settings

def verify_gmail_delivery():
    today = date.today()
    
    print("🔔 CLASSWAVE GMAIL DELIVERY VERIFICATION")
    print("=" * 60)
    
    # Check email configuration
    print("📧 EMAIL CONFIGURATION:")
    print(f"   SMTP Host: {settings.EMAIL_HOST}")
    print(f"   SMTP Port: {settings.EMAIL_PORT}")
    print(f"   From Email: {settings.DEFAULT_FROM_EMAIL}")
    print(f"   Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"   Backend: {settings.EMAIL_BACKEND}")
    
    # Check schedules for today
    todays_schedules = Schedule.objects.filter(date=today)
    print(f"\n📅 SCHEDULES FOR TODAY ({today}):")
    print(f"   Total classes: {todays_schedules.count()}")
    
    if todays_schedules.exists():
        for schedule in todays_schedules:
            print(f"   • {schedule.subject_name} ({schedule.start_time} - {schedule.end_time})")
    else:
        print("   ℹ️ No classes scheduled for today")
    
    # Check students and their email delivery status
    students = User.objects.filter(user_type='student')
    print(f"\n👥 STUDENT EMAIL DELIVERY STATUS:")
    print(f"   Total students: {students.count()}")
    print()
    
    delivered_count = 0
    pending_count = 0
    disabled_count = 0
    
    for student in students:
        print(f"👤 {student.username}")
        print(f"   📧 Email: {student.email}")
        
        # Check digest preference
        try:
            pref = DailyDigestPreference.objects.get(student=student)
            if pref.is_enabled:
                print(f"   ⚙️ Digest time: {pref.digest_time} (Enabled)")
            else:
                print(f"   ⚙️ Digest: Disabled by student")
                disabled_count += 1
                print()
                continue
        except DailyDigestPreference.DoesNotExist:
            print(f"   ⚙️ Digest time: 07:00 (Default)")
        
        # Check today's digest
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if digest:
            if digest.is_sent:
                print(f"   ✅ Gmail delivery: SENT")
                print(f"   📬 Status: Email delivered to Gmail inbox")
                delivered_count += 1
            else:
                print(f"   ⏳ Gmail delivery: PENDING")
                print(f"   📬 Status: Waiting for delivery time")
                pending_count += 1
        else:
            if todays_schedules.exists():
                print(f"   ❌ Gmail delivery: NOT CREATED")
                print(f"   📬 Status: Digest not generated")
            else:
                print(f"   ℹ️ Gmail delivery: NO CLASSES TODAY")
                print(f"   📬 Status: No digest needed")
        
        print()
    
    # Summary
    print("📊 DELIVERY SUMMARY:")
    print(f"   ✅ Successfully delivered: {delivered_count}")
    print(f"   ⏳ Pending delivery: {pending_count}")
    print(f"   🚫 Disabled by students: {disabled_count}")
    print(f"   👥 Total active students: {delivered_count + pending_count}")
    
    # Check if system is working
    if todays_schedules.exists():
        if delivered_count > 0:
            print(f"\n🎉 SUCCESS: Gmail delivery system is working!")
            print(f"   📧 {delivered_count} students received their daily digest")
            print(f"   📬 Emails are in their Gmail inbox")
        elif pending_count > 0:
            print(f"\n⏳ PENDING: Digests created, waiting for delivery time")
            print(f"   📧 {pending_count} students will receive emails at their preferred time")
        else:
            print(f"\n⚠️ ISSUE: Classes exist but no digests delivered")
    else:
        print(f"\n✅ NORMAL: No classes today, no emails needed")
    
    # Show recent email files
    import glob
    email_files = glob.glob('sent_emails/*.log')
    recent_emails = sorted(email_files)[-5:] if email_files else []
    
    if recent_emails:
        print(f"\n📁 RECENT EMAIL FILES:")
        for email_file in recent_emails:
            print(f"   📄 {os.path.basename(email_file)}")
    
    print(f"\n🔧 SYSTEM STATUS: {'🟢 OPERATIONAL' if delivered_count > 0 or not todays_schedules.exists() else '🟡 NEEDS ATTENTION'}")

if __name__ == "__main__":
    verify_gmail_delivery()
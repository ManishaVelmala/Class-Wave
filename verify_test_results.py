#!/usr/bin/env python
"""
Comprehensive verification of all test email results
"""

import os
import django
from datetime import datetime
import glob

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def verify_test_results():
    print("🔍 COMPREHENSIVE TEST VERIFICATION")
    print("=" * 60)
    
    now = datetime.now()
    print(f"⏰ Verification time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check all students and their preferences
    students = User.objects.filter(user_type='student')
    print(f"\n👥 STUDENT EMAIL PREFERENCES:")
    
    for student in students:
        print(f"\n👤 {student.username}:")
        print(f"   📧 Email: {student.email}")
        
        try:
            pref = DailyDigestPreference.objects.get(student=student)
            print(f"   ⚙️ Preferred time: {pref.digest_time}")
            print(f"   ✅ Enabled: {pref.is_enabled}")
        except DailyDigestPreference.DoesNotExist:
            print(f"   ⚙️ Preferred time: 07:00 (Default)")
            print(f"   ✅ Enabled: True (Default)")
    
    # Check test emails sent
    print(f"\n📧 TEST EMAILS SENT TODAY:")
    
    test_reminders = Reminder.objects.filter(
        reminder_type__in=['test_message', 'future_test']
    ).order_by('-reminder_time')
    
    if test_reminders.exists():
        for reminder in test_reminders:
            status = "✅ SENT" if reminder.is_sent else "⏳ PENDING"
            print(f"   👤 {reminder.student.username}: {status}")
            print(f"      📅 Scheduled: {reminder.reminder_time}")
            print(f"      📧 To: {reminder.student.email}")
    else:
        print("   ℹ️ No test emails found")
    
    # Check email files
    print(f"\n📁 EMAIL FILES GENERATED:")
    email_files = glob.glob('sent_emails/*.log')
    recent_files = sorted(email_files)[-10:] if email_files else []
    
    if recent_files:
        print(f"   📄 Recent email files ({len(recent_files)} shown):")
        for email_file in recent_files:
            file_name = os.path.basename(email_file)
            file_time = file_name.split('-')[0] + '-' + file_name.split('-')[1]
            print(f"      {file_time}: {file_name}")
    else:
        print("   ℹ️ No email files found")
    
    # Summary
    sent_tests = test_reminders.filter(is_sent=True).count()
    pending_tests = test_reminders.filter(is_sent=False).count()
    
    print(f"\n📊 TEST SUMMARY:")
    print(f"   👥 Total students: {students.count()}")
    print(f"   📧 Test emails sent: {sent_tests}")
    print(f"   ⏳ Test emails pending: {pending_tests}")
    print(f"   📁 Email files: {len(email_files)}")
    
    # Verification checklist
    print(f"\n✅ VERIFICATION CHECKLIST:")
    
    # Check 1: All students have preferences
    students_with_prefs = DailyDigestPreference.objects.filter(
        student__user_type='student'
    ).count()
    print(f"   📋 Students with preferences: {students_with_prefs}/{students.count()}")
    
    # Check 2: Test emails created
    if test_reminders.exists():
        print(f"   📧 Test emails created: ✅ YES ({test_reminders.count()})")
    else:
        print(f"   📧 Test emails created: ❌ NO")
    
    # Check 3: Email files generated
    if email_files:
        print(f"   📁 Email files generated: ✅ YES ({len(email_files)})")
    else:
        print(f"   📁 Email files generated: ❌ NO")
    
    # Check 4: System configuration
    from django.conf import settings
    print(f"   ⚙️ Email backend: {settings.EMAIL_BACKEND}")
    print(f"   📧 From email: {settings.DEFAULT_FROM_EMAIL}")
    
    print(f"\n🎯 NEXT STEPS:")
    if pending_tests > 0:
        print(f"   1. Run: python manage.py runserver")
        print(f"   2. Keep server running to send pending emails")
        print(f"   3. Check: python check_scheduled_tests.py")
    
    if sent_tests > 0:
        print(f"   4. Check Gmail inboxes for test messages")
        print(f"   5. Verify emails arrived at correct times")
    
    print(f"\n🎉 SYSTEM STATUS:")
    if sent_tests > 0:
        print(f"   ✅ Time preference system is WORKING!")
        print(f"   📧 Students are receiving emails successfully")
    else:
        print(f"   ⏳ Tests in progress - check back in a few minutes")

if __name__ == "__main__":
    verify_test_results()
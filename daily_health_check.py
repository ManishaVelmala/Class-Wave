#!/usr/bin/env python3
import os, sys, django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def daily_health_check():
    print("DAILY EMAIL SYSTEM HEALTH CHECK")
    print("=" * 36)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    current_india_time = india_now.time()
    
    print(f"Health check for: {india_date}")
    print(f"Current India time: {current_india_time.strftime('%I:%M %p')}")
    
    # Check students and preferences
    students = User.objects.filter(user_type='student')
    preferences = DailyDigestPreference.objects.filter(is_enabled=True)
    
    print(f"\n1. STUDENT PREFERENCES:")
    print(f"   Total students: {students.count()}")
    print(f"   Active preferences: {preferences.count()}")
    
    # Check digests
    digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date
    )
    
    print(f"\n2. DIGEST GENERATION:")
    print(f"   Digests for today: {digests.count()}")
    
    # Check email delivery
    sent_digests = digests.filter(is_sent=True)
    pending_digests = digests.filter(is_sent=False)
    
    print(f"\n3. EMAIL DELIVERY:")
    print(f"   Sent: {sent_digests.count()}")
    print(f"   Pending: {pending_digests.count()}")
    
    # Check overdue emails
    overdue_count = 0
    for digest in pending_digests:
        try:
            pref = DailyDigestPreference.objects.get(student=digest.student, is_enabled=True)
            if current_india_time >= pref.digest_time:
                overdue_count += 1
        except DailyDigestPreference.DoesNotExist:
            continue
    
    print(f"\n4. OVERDUE EMAILS:")
    if overdue_count > 0:
        print(f"   🚨 {overdue_count} emails overdue!")
    else:
        print(f"   ✅ No overdue emails")
    
    # Test Gmail connection
    print(f"\n5. GMAIL CONNECTION:")
    try:
        send_mail(
            subject='Health Check Test',
            message='This is a health check test email.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        print(f"   ✅ Gmail connection working")
    except Exception as e:
        print(f"   ❌ Gmail connection failed: {str(e)[:50]}...")
    
    # Overall health
    issues = 0
    if preferences.count() < students.count():
        issues += 1
    if digests.count() < students.count():
        issues += 1
    if overdue_count > 0:
        issues += 1
    
    print(f"\n🎯 OVERALL HEALTH:")
    if issues == 0:
        print(f"   ✅ EXCELLENT - No issues found")
    elif issues <= 2:
        print(f"   ⚠️  GOOD - {issues} minor issues")
    else:
        print(f"   🚨 NEEDS ATTENTION - {issues} issues found")
    
    return issues

if __name__ == "__main__":
    issues = daily_health_check()
    
    if issues > 0:
        print(f"\n🔧 RECOMMENDED ACTIONS:")
        print("1. Run: python enhanced_email_monitor.py")
        print("2. Check individual students with issues")
        print("3. Verify Gmail SMTP settings")
    
    print(f"\n✅ HEALTH CHECK COMPLETE")

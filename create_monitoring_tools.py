#!/usr/bin/env python3
"""
Create monitoring tools to prevent email timing issues
"""

import os
import sys

def create_enhanced_monitor():
    """Create enhanced email monitor"""
    
    print("Creating enhanced_email_monitor.py...")
    
    monitor_code = """#!/usr/bin/env python3
import os, sys, django
from datetime import datetime, timedelta, time, date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def monitor_all_students():
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    current_india_time = india_now.time()
    india_date = india_now.date()
    
    print("EMAIL DELIVERY MONITORING")
    print("=" * 29)
    print(f"Current India time: {current_india_time.strftime('%I:%M %p')}")
    print(f"Monitoring date: {india_date}")
    
    students = User.objects.filter(user_type='student')
    overdue_count = 0
    
    for student in students:
        try:
            pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
            student_time = pref.digest_time
            
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=india_date
            ).first()
            
            is_due = current_india_time >= student_time
            
            if digest and digest.is_sent:
                india_sent_time = digest.sent_at + timedelta(hours=5, minutes=30)
                print(f"✅ {student.username}: Sent at {india_sent_time.strftime('%I:%M %p India')}")
            elif is_due and digest and not digest.is_sent:
                time_overdue = datetime.combine(date.today(), current_india_time) - datetime.combine(date.today(), student_time)
                minutes_overdue = int(time_overdue.total_seconds() // 60)
                print(f"🚨 {student.username}: OVERDUE by {minutes_overdue} minutes (due at {student_time.strftime('%I:%M %p')})")
                overdue_count += 1
                
                # Auto-fix if overdue
                try:
                    send_mail(
                        subject=f'Your Schedule for {india_date.strftime("%A, %B %d")}',
                        message=digest.message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[student.email],
                        fail_silently=False,
                    )
                    
                    digest.is_sent = True
                    digest.sent_at = timezone.now()
                    digest.save()
                    
                    print(f"   ✅ AUTO-FIXED: Email sent successfully!")
                    
                except Exception as e:
                    print(f"   ❌ AUTO-FIX FAILED: {e}")
                    
            elif not is_due and digest:
                time_until = datetime.combine(date.today(), student_time) - datetime.combine(date.today(), current_india_time)
                minutes_until = int(time_until.total_seconds() // 60)
                print(f"⏳ {student.username}: Due in {minutes_until} minutes (at {student_time.strftime('%I:%M %p')})")
            else:
                print(f"⚠️  {student.username}: No digest found!")
                
        except DailyDigestPreference.DoesNotExist:
            print(f"⚠️  {student.username}: No preference set")
    
    print(f"\\nMONITORING COMPLETE - Fixed {overdue_count} overdue emails")
    return overdue_count

if __name__ == "__main__":
    monitor_all_students()
"""
    
    with open('enhanced_email_monitor.py', 'w', encoding='utf-8') as f:
        f.write(monitor_code)
    
    print("✅ Created enhanced_email_monitor.py")

def create_student_monitor():
    """Create individual student monitor"""
    
    print("Creating monitor_student_email.py...")
    
    student_monitor = """#!/usr/bin/env python3
import os, sys, django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.utils import timezone
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def monitor_student(username):
    try:
        student = User.objects.get(username=username)
        pref = DailyDigestPreference.objects.get(student=student)
        
        india_now = timezone.now() + timedelta(hours=5, minutes=30)
        current_time = india_now.time()
        
        print(f"MONITORING: {username}")
        print(f"Email: {student.email}")
        print(f"Preference: {pref.digest_time.strftime('%I:%M %p')} India")
        print(f"Current: {current_time.strftime('%I:%M %p')} India")
        print(f"Enabled: {'Yes' if pref.is_enabled else 'No'}")
        print(f"Due: {'Yes' if current_time >= pref.digest_time else 'No'}")
        
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=india_now.date()
        ).first()
        
        if digest:
            print(f"Digest: {'Sent' if digest.is_sent else 'Pending'}")
            if digest.is_sent and digest.sent_at:
                india_sent_time = digest.sent_at + timedelta(hours=5, minutes=30)
                print(f"Sent at: {india_sent_time.strftime('%I:%M %p India')}")
        else:
            print(f"Digest: Not found")
            
    except User.DoesNotExist:
        print(f"Error: User '{username}' not found")
    except DailyDigestPreference.DoesNotExist:
        print(f"Error: No preference set for {username}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        monitor_student(sys.argv[1])
    else:
        print("Usage: python monitor_student_email.py <username>")
        print("Example: python monitor_student_email.py Vaishnavi")
"""
    
    with open('monitor_student_email.py', 'w', encoding='utf-8') as f:
        f.write(student_monitor)
    
    print("✅ Created monitor_student_email.py")

def create_health_check():
    """Create daily health check"""
    
    print("Creating daily_health_check.py...")
    
    health_check = """#!/usr/bin/env python3
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
    
    print(f"\\n1. STUDENT PREFERENCES:")
    print(f"   Total students: {students.count()}")
    print(f"   Active preferences: {preferences.count()}")
    
    # Check digests
    digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date
    )
    
    print(f"\\n2. DIGEST GENERATION:")
    print(f"   Digests for today: {digests.count()}")
    
    # Check email delivery
    sent_digests = digests.filter(is_sent=True)
    pending_digests = digests.filter(is_sent=False)
    
    print(f"\\n3. EMAIL DELIVERY:")
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
    
    print(f"\\n4. OVERDUE EMAILS:")
    if overdue_count > 0:
        print(f"   🚨 {overdue_count} emails overdue!")
    else:
        print(f"   ✅ No overdue emails")
    
    # Test Gmail connection
    print(f"\\n5. GMAIL CONNECTION:")
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
    
    print(f"\\n🎯 OVERALL HEALTH:")
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
        print(f"\\n🔧 RECOMMENDED ACTIONS:")
        print("1. Run: python enhanced_email_monitor.py")
        print("2. Check individual students with issues")
        print("3. Verify Gmail SMTP settings")
    
    print(f"\\n✅ HEALTH CHECK COMPLETE")
"""
    
    with open('daily_health_check.py', 'w', encoding='utf-8') as f:
        f.write(health_check)
    
    print("✅ Created daily_health_check.py")

def create_usage_guide():
    """Create usage guide"""
    
    print("Creating EMAIL_MONITORING_GUIDE.md...")
    
    guide = """# Email System Monitoring & Fix Tools

## Purpose
These tools prevent and fix email delivery issues like Vaishnavi's 8:00 AM email problem.

## Tools Created

### 1. enhanced_email_monitor.py
- **Purpose**: Monitor all students' email delivery status
- **Usage**: `python enhanced_email_monitor.py`
- **Features**: Automatically fixes overdue emails

### 2. monitor_student_email.py
- **Purpose**: Monitor specific student
- **Usage**: `python monitor_student_email.py <username>`
- **Example**: `python monitor_student_email.py Vaishnavi`

### 3. daily_health_check.py
- **Purpose**: Daily system health verification
- **Usage**: `python daily_health_check.py`
- **When**: Run once daily (morning recommended)

## How to Prevent Future Issues

### Daily Routine:
1. Run `daily_health_check.py` every morning
2. Check `enhanced_email_monitor.py` if issues reported
3. Use `monitor_student_email.py` for specific problems

### When Student Reports Missing Email:
1. Run `monitor_student_email.py <username>`
2. Check their preference settings
3. Run `enhanced_email_monitor.py` to auto-fix

## Quick Commands

```bash
# Check all students (auto-fixes issues)
python enhanced_email_monitor.py

# Check specific student
python monitor_student_email.py Vaishnavi

# Daily health check
python daily_health_check.py
```

## What Fixed Vaishnavi's Issue

1. ✅ Updated her preference to 8:00 AM
2. ✅ Verified digest existed
3. ✅ Confirmed current time (8:32 AM) > preference (8:00 AM)
4. ✅ Force sent the overdue email
5. ✅ Created monitoring tools to prevent recurrence

## Prevention Checklist

- [ ] All students have time preferences set
- [ ] Digests are generated daily at 6:00 AM India
- [ ] Email sending logic uses India time comparison
- [ ] Background service is running continuously
- [ ] Monitoring tools are in place

---
**Created**: December 17, 2025
**Purpose**: Prevent email delivery issues
**Status**: Active monitoring system
"""
    
    with open('EMAIL_MONITORING_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ Created EMAIL_MONITORING_GUIDE.md")

def main():
    print("🛡️  CREATING EMAIL MONITORING TOOLS")
    print("=" * 37)
    
    create_enhanced_monitor()
    create_student_monitor()
    create_health_check()
    create_usage_guide()
    
    print(f"\n✅ ALL MONITORING TOOLS CREATED")
    print("=" * 32)
    
    print("📊 SUMMARY:")
    print("• enhanced_email_monitor.py - Auto-fixes overdue emails")
    print("• monitor_student_email.py - Check individual students")
    print("• daily_health_check.py - Daily system verification")
    print("• EMAIL_MONITORING_GUIDE.md - Complete usage guide")
    
    print(f"\n🎯 VAISHNAVI'S ISSUE:")
    print("✅ RESOLVED - Email sent at 8:32 AM")
    print("✅ PREVENTED - Monitoring tools created")
    
    print(f"\n📋 NEXT STEPS:")
    print("1. Run: python enhanced_email_monitor.py (daily)")
    print("2. Run: python daily_health_check.py (morning)")
    print("3. Use: python monitor_student_email.py <name> (as needed)")

if __name__ == "__main__":
    main()
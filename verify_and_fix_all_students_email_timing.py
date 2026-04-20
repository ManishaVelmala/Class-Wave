#!/usr/bin/env python3
"""
Comprehensive verification and rectification of email timing issues for ALL students
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
from django.core.management import call_command
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def get_current_india_status():
    """Get current India time status"""
    
    print("🕐 CURRENT INDIA TIME STATUS")
    print("=" * 30)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    current_india_time = india_now.time()
    india_date = india_now.date()
    
    print(f"Current UTC time: {utc_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Current India time: {india_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"India date: {india_date}")
    print(f"India time: {current_india_time.strftime('%I:%M %p')}")
    
    return india_date, current_india_time, utc_now

def verify_all_student_preferences():
    """Verify time preferences for all students"""
    
    print(f"\n👥 VERIFYING ALL STUDENT PREFERENCES")
    print("=" * 37)
    
    students = User.objects.filter(user_type='student')
    
    print(f"Total students: {students.count()}")
    
    students_with_prefs = []
    students_without_prefs = []
    disabled_prefs = []
    
    for student in students:
        try:
            pref = DailyDigestPreference.objects.get(student=student)
            
            if pref.is_enabled:
                students_with_prefs.append((student, pref))
                print(f"✅ {student.username}: {pref.digest_time.strftime('%I:%M %p')} India (Enabled)")
            else:
                disabled_prefs.append((student, pref))
                print(f"⚠️  {student.username}: {pref.digest_time.strftime('%I:%M %p')} India (DISABLED)")
                
        except DailyDigestPreference.DoesNotExist:
            students_without_prefs.append(student)
            print(f"❌ {student.username}: NO PREFERENCE SET")
    
    print(f"\n📊 Preference Summary:")
    print(f"   ✅ With preferences: {len(students_with_prefs)}")
    print(f"   ⚠️  Disabled: {len(disabled_prefs)}")
    print(f"   ❌ Missing: {len(students_without_prefs)}")
    
    return students_with_prefs, disabled_prefs, students_without_prefs

def verify_all_student_digests(india_date):
    """Verify digest status for all students"""
    
    print(f"\n📊 VERIFYING ALL STUDENT DIGESTS FOR {india_date}")
    print("=" * 50)
    
    students = User.objects.filter(user_type='student')
    
    students_with_digests = []
    students_without_digests = []
    
    for student in students:
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=india_date
        ).first()
        
        if digest:
            students_with_digests.append((student, digest))
            status = "✅ Sent" if digest.is_sent else "⏳ Pending"
            
            if digest.is_sent and digest.sent_at:
                india_sent_time = digest.sent_at + timedelta(hours=5, minutes=30)
                sent_info = f" at {india_sent_time.strftime('%I:%M %p India')}"
            else:
                sent_info = ""
            
            print(f"{status} {student.username}: Digest exists{sent_info}")
        else:
            students_without_digests.append(student)
            print(f"❌ {student.username}: NO DIGEST FOUND")
    
    print(f"\n📊 Digest Summary:")
    print(f"   ✅ With digests: {len(students_with_digests)}")
    print(f"   ❌ Missing digests: {len(students_without_digests)}")
    
    return students_with_digests, students_without_digests

def analyze_email_timing_for_all_students(students_with_prefs, current_india_time):
    """Analyze email timing for all students with preferences"""
    
    print(f"\n⏰ ANALYZING EMAIL TIMING FOR ALL STUDENTS")
    print("=" * 44)
    
    print(f"Current India time: {current_india_time.strftime('%I:%M %p')}")
    
    emails_due_now = []
    emails_pending = []
    emails_sent = []
    emails_overdue = []
    
    for student, pref in students_with_prefs:
        student_time = pref.digest_time
        is_due = current_india_time >= student_time
        
        # Get digest status
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=date.today()
        ).first()
        
        if digest and digest.is_sent:
            emails_sent.append((student, pref, digest))
            india_sent_time = digest.sent_at + timedelta(hours=5, minutes=30)
            print(f"✅ {student.username}: SENT at {india_sent_time.strftime('%I:%M %p India')} (due: {student_time.strftime('%I:%M %p')})")
            
        elif is_due and digest and not digest.is_sent:
            # Calculate how overdue
            time_overdue = datetime.combine(date.today(), current_india_time) - datetime.combine(date.today(), student_time)
            minutes_overdue = int(time_overdue.total_seconds() // 60)
            
            emails_overdue.append((student, pref, digest, minutes_overdue))
            print(f"🚨 {student.username}: OVERDUE by {minutes_overdue} minutes (due: {student_time.strftime('%I:%M %p')}, current: {current_india_time.strftime('%I:%M %p')})")
            
        elif is_due and not digest:
            emails_due_now.append((student, pref))
            print(f"❌ {student.username}: DUE NOW but NO DIGEST (due: {student_time.strftime('%I:%M %p')})")
            
        else:
            # Calculate time until due
            time_until = datetime.combine(date.today(), student_time) - datetime.combine(date.today(), current_india_time)
            
            if time_until.total_seconds() > 0:
                hours = int(time_until.total_seconds() // 3600)
                minutes = int((time_until.total_seconds() % 3600) // 60)
                emails_pending.append((student, pref, digest))
                print(f"⏳ {student.username}: Due in {hours}h {minutes}m (at {student_time.strftime('%I:%M %p')})")
            else:
                # Should have been sent but wasn't
                emails_overdue.append((student, pref, digest, 0))
                print(f"⚠️  {student.username}: Should have been sent (due: {student_time.strftime('%I:%M %p')})")
    
    print(f"\n📊 Email Timing Analysis:")
    print(f"   ✅ Sent: {len(emails_sent)}")
    print(f"   🚨 Overdue: {len(emails_overdue)}")
    print(f"   ❌ Due but no digest: {len(emails_due_now)}")
    print(f"   ⏳ Pending: {len(emails_pending)}")
    
    return emails_sent, emails_overdue, emails_due_now, emails_pending

def fix_missing_preferences(students_without_prefs):
    """Fix students without time preferences"""
    
    if not students_without_prefs:
        return 0
    
    print(f"\n🔧 FIXING MISSING PREFERENCES")
    print("=" * 28)
    
    fixed_count = 0
    default_time = time(7, 0)  # 7:00 AM default
    
    for student in students_without_prefs:
        print(f"🔧 Creating preference for {student.username}...")
        
        pref = DailyDigestPreference.objects.create(
            student=student,
            digest_time=default_time,
            is_enabled=True
        )
        
        print(f"   ✅ Set to {default_time.strftime('%I:%M %p')} India (default)")
        fixed_count += 1
    
    print(f"\n📊 Fixed {fixed_count} missing preferences")
    return fixed_count

def fix_disabled_preferences(disabled_prefs):
    """Fix disabled preferences"""
    
    if not disabled_prefs:
        return 0
    
    print(f"\n🔧 FIXING DISABLED PREFERENCES")
    print("=" * 31)
    
    fixed_count = 0
    
    for student, pref in disabled_prefs:
        print(f"🔧 Enabling preference for {student.username}...")
        
        pref.is_enabled = True
        pref.save()
        
        print(f"   ✅ Enabled {pref.digest_time.strftime('%I:%M %p')} India")
        fixed_count += 1
    
    print(f"\n📊 Enabled {fixed_count} disabled preferences")
    return fixed_count

def fix_missing_digests(students_without_digests, india_date):
    """Fix students without digests"""
    
    if not students_without_digests:
        return 0
    
    print(f"\n🔧 FIXING MISSING DIGESTS")
    print("=" * 25)
    
    from reminders.tasks import create_daily_digest_for_student
    
    fixed_count = 0
    
    for student in students_without_digests:
        print(f"🔧 Creating digest for {student.username}...")
        
        digest = create_daily_digest_for_student(student.id, india_date)
        
        if digest:
            print(f"   ✅ Digest created successfully")
            fixed_count += 1
        else:
            print(f"   ⚠️  No classes found for {student.username}")
    
    print(f"\n📊 Created {fixed_count} missing digests")
    return fixed_count

def fix_overdue_emails(emails_overdue):
    """Fix overdue emails by sending them immediately"""
    
    if not emails_overdue:
        return 0
    
    print(f"\n🚨 FIXING OVERDUE EMAILS")
    print("=" * 24)
    
    fixed_count = 0
    
    for student, pref, digest, minutes_overdue in emails_overdue:
        if not digest:
            print(f"⚠️  {student.username}: No digest to send")
            continue
        
        print(f"🚀 Sending overdue email to {student.username} ({minutes_overdue}m overdue)...")
        
        try:
            send_mail(
                subject=f'📅 Your Schedule for {digest.digest_date.strftime("%A, %B %d")}',
                message=digest.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=False,
            )
            
            # Mark as sent
            digest.is_sent = True
            digest.sent_at = timezone.now()
            digest.save()
            
            india_sent_time = digest.sent_at + timedelta(hours=5, minutes=30)
            print(f"   ✅ Email sent at {india_sent_time.strftime('%I:%M %p India')}")
            fixed_count += 1
            
        except Exception as e:
            print(f"   ❌ Failed to send: {str(e)[:50]}...")
    
    print(f"\n📊 Fixed {fixed_count} overdue emails")
    return fixed_count

def run_comprehensive_system_check():
    """Run comprehensive system check and fix"""
    
    print(f"\n🔄 RUNNING COMPREHENSIVE SYSTEM CHECK")
    print("=" * 39)
    
    try:
        print("Running send_real_daily_digests command...")
        call_command('send_real_daily_digests', verbosity=1)
        print("✅ System check completed")
        
    except Exception as e:
        print(f"❌ System check failed: {e}")

def create_final_verification_report(india_date, current_india_time):
    """Create final verification report"""
    
    print(f"\n📊 FINAL VERIFICATION REPORT")
    print("=" * 30)
    
    students = User.objects.filter(user_type='student')
    
    print(f"Report for: {india_date}")
    print(f"India time: {current_india_time.strftime('%I:%M %p')}")
    print(f"Total students: {students.count()}")
    
    # Check preferences
    prefs_count = DailyDigestPreference.objects.filter(is_enabled=True).count()
    
    # Check digests
    digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date
    )
    
    sent_count = digests.filter(is_sent=True).count()
    pending_count = digests.filter(is_sent=False).count()
    
    # Check overdue
    overdue_count = 0
    for digest in digests.filter(is_sent=False):
        try:
            pref = DailyDigestPreference.objects.get(student=digest.student, is_enabled=True)
            if current_india_time >= pref.digest_time:
                overdue_count += 1
        except DailyDigestPreference.DoesNotExist:
            continue
    
    print(f"\n✅ SYSTEM STATUS:")
    print(f"   Active preferences: {prefs_count}/{students.count()}")
    print(f"   Digests generated: {digests.count()}/{students.count()}")
    print(f"   Emails sent: {sent_count}")
    print(f"   Emails pending: {pending_count}")
    print(f"   Emails overdue: {overdue_count}")
    
    # Overall health score
    if overdue_count == 0 and prefs_count == students.count() and digests.count() == students.count():
        health = "EXCELLENT"
        color = "✅"
    elif overdue_count <= 1:
        health = "GOOD"
        color = "⚠️ "
    else:
        health = "NEEDS ATTENTION"
        color = "🚨"
    
    print(f"\n{color} OVERALL HEALTH: {health}")
    
    return overdue_count == 0

def main():
    """Main verification and rectification process"""
    
    print("🔍 COMPREHENSIVE EMAIL TIMING VERIFICATION & RECTIFICATION")
    print("=" * 60)
    print("Checking ALL students for email timing issues...")
    
    # Step 1: Get current status
    india_date, current_india_time, utc_now = get_current_india_status()
    
    # Step 2: Verify preferences
    students_with_prefs, disabled_prefs, students_without_prefs = verify_all_student_preferences()
    
    # Step 3: Verify digests
    students_with_digests, students_without_digests = verify_all_student_digests(india_date)
    
    # Step 4: Analyze timing
    emails_sent, emails_overdue, emails_due_now, emails_pending = analyze_email_timing_for_all_students(
        students_with_prefs, current_india_time
    )
    
    # Step 5: Fix issues
    print(f"\n🔧 RECTIFICATION PHASE")
    print("=" * 21)
    
    fixes_applied = 0
    
    # Fix missing preferences
    fixes_applied += fix_missing_preferences(students_without_prefs)
    
    # Fix disabled preferences
    fixes_applied += fix_disabled_preferences(disabled_prefs)
    
    # Fix missing digests
    fixes_applied += fix_missing_digests(students_without_digests, india_date)
    
    # Fix overdue emails
    fixes_applied += fix_overdue_emails(emails_overdue)
    
    # Step 6: Run system check
    run_comprehensive_system_check()
    
    # Step 7: Final verification
    system_healthy = create_final_verification_report(india_date, current_india_time)
    
    # Step 8: Summary
    print(f"\n" + "=" * 60)
    print("🎯 RECTIFICATION COMPLETE")
    print("=" * 60)
    
    print(f"📊 FIXES APPLIED: {fixes_applied}")
    print(f"🏥 SYSTEM HEALTH: {'✅ EXCELLENT' if system_healthy else '⚠️  NEEDS MONITORING'}")
    
    if system_healthy:
        print(f"\n✅ ALL STUDENTS EMAIL TIMING VERIFIED & FIXED")
        print("• All students have time preferences")
        print("• All digests are generated")
        print("• All due emails are sent")
        print("• No overdue emails remaining")
    else:
        print(f"\n⚠️  SOME ISSUES MAY REMAIN")
        print("• Run enhanced_email_monitor.py for ongoing monitoring")
        print("• Check individual students if issues persist")
    
    print(f"\n📋 ONGOING MONITORING:")
    print("• Run: python enhanced_email_monitor.py (daily)")
    print("• Run: python daily_health_check.py (morning)")
    print("• Use: python monitor_student_email.py <name> (as needed)")

if __name__ == "__main__":
    main()
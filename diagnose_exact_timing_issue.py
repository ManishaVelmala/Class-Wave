#!/usr/bin/env python3
"""
Diagnose Exact Timing Issue - Check why emails aren't sent at exact preference times
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.utils import timezone
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def check_exact_timing_for_all_students():
    """Check exact timing for all students"""
    
    print("🔍 DIAGNOSING EXACT TIMING ISSUE")
    print("=" * 34)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    current_time = india_now.time()
    
    print(f"Current India time: {current_time.strftime('%I:%M %p')}")
    print(f"Current India date: {india_date}")
    
    students = User.objects.filter(user_type='student')
    
    timing_issues = []
    
    for student in students:
        try:
            pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=india_date
            ).first()
            
            print(f"\n👤 {student.username}:")
            print(f"   Preference: {pref.digest_time.strftime('%I:%M %p')}")
            
            if digest and digest.is_sent:
                # Convert sent time to India time
                sent_utc = digest.sent_at
                sent_india = sent_utc + timedelta(hours=5, minutes=30)
                sent_time = sent_india.time()
                
                print(f"   Sent at: {sent_time.strftime('%I:%M %p')} India")
                
                # Calculate timing difference
                pref_datetime = datetime.combine(india_date, pref.digest_time)
                sent_datetime = datetime.combine(india_date, sent_time)
                
                time_diff = sent_datetime - pref_datetime
                diff_seconds = time_diff.total_seconds()
                diff_minutes = diff_seconds / 60
                
                if abs(diff_minutes) > 1:  # More than 1 minute difference
                    if diff_minutes > 0:
                        print(f"   ⚠️  LATE by {diff_minutes:.1f} minutes")
                    else:
                        print(f"   ⚠️  EARLY by {abs(diff_minutes):.1f} minutes")
                    
                    timing_issues.append({
                        'student': student.username,
                        'preference': pref.digest_time,
                        'sent_time': sent_time,
                        'diff_minutes': diff_minutes
                    })
                else:
                    print(f"   ✅ EXACT TIMING (within 1 minute)")
                    
            elif digest and not digest.is_sent:
                # Check if it should have been sent already
                if current_time >= pref.digest_time:
                    time_overdue = datetime.combine(india_date, current_time) - datetime.combine(india_date, pref.digest_time)
                    overdue_minutes = time_overdue.total_seconds() / 60
                    
                    print(f"   🚨 NOT SENT - {overdue_minutes:.1f} minutes overdue!")
                    
                    timing_issues.append({
                        'student': student.username,
                        'preference': pref.digest_time,
                        'sent_time': None,
                        'diff_minutes': overdue_minutes,
                        'status': 'overdue'
                    })
                else:
                    time_until = datetime.combine(india_date, pref.digest_time) - datetime.combine(india_date, current_time)
                    minutes_until = time_until.total_seconds() / 60
                    
                    print(f"   ⏳ PENDING - {minutes_until:.1f} minutes until send time")
            else:
                print(f"   ❓ NO DIGEST CREATED")
                
        except DailyDigestPreference.DoesNotExist:
            print(f"\n👤 {student.username}:")
            print(f"   ❌ NO PREFERENCE SET")
    
    return timing_issues

def check_service_timing_accuracy():
    """Check if the service is checking at the right intervals"""
    
    print(f"\n⏰ SERVICE TIMING ACCURACY CHECK")
    print("=" * 33)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    current_time = india_now.time()
    
    print(f"Current time: {current_time.strftime('%H:%M:%S')}")
    
    # Check how close we are to 30-second intervals
    seconds = current_time.second
    next_30_check = 30 - (seconds % 30)
    
    print(f"Seconds: {seconds}")
    print(f"Next 30s check in: {next_30_check} seconds")
    
    if next_30_check <= 5:
        print("✅ Service should check very soon (within 5 seconds)")
    elif next_30_check <= 15:
        print("⏳ Service will check soon (within 15 seconds)")
    else:
        print("⏰ Service will check in a while")
    
    return next_30_check

def analyze_timing_patterns(timing_issues):
    """Analyze timing patterns to identify root cause"""
    
    print(f"\n📊 TIMING PATTERN ANALYSIS")
    print("=" * 27)
    
    if not timing_issues:
        print("✅ No timing issues found - all emails sent at exact times!")
        return
    
    print(f"Found {len(timing_issues)} timing issues:")
    
    early_emails = [issue for issue in timing_issues if issue.get('diff_minutes', 0) < -1]
    late_emails = [issue for issue in timing_issues if issue.get('diff_minutes', 0) > 1]
    overdue_emails = [issue for issue in timing_issues if issue.get('status') == 'overdue']
    
    if early_emails:
        print(f"\n🚨 EARLY EMAILS ({len(early_emails)}):")
        for issue in early_emails:
            print(f"   • {issue['student']}: {abs(issue['diff_minutes']):.1f} min early")
        print("   💡 Cause: Service sending emails before preference time")
    
    if late_emails:
        print(f"\n⏰ LATE EMAILS ({len(late_emails)}):")
        for issue in late_emails:
            print(f"   • {issue['student']}: {issue['diff_minutes']:.1f} min late")
        print("   💡 Cause: Service delay or timing logic issue")
    
    if overdue_emails:
        print(f"\n🚨 OVERDUE EMAILS ({len(overdue_emails)}):")
        for issue in overdue_emails:
            print(f"   • {issue['student']}: {issue['diff_minutes']:.1f} min overdue")
        print("   💡 Cause: Service not running or major timing issue")

def provide_timing_solutions(timing_issues):
    """Provide solutions based on timing issues found"""
    
    print(f"\n🔧 TIMING SOLUTIONS")
    print("=" * 17)
    
    if not timing_issues:
        print("✅ No solutions needed - timing is perfect!")
        return
    
    # Check for overdue emails (service not running)
    overdue_emails = [issue for issue in timing_issues if issue.get('status') == 'overdue']
    if overdue_emails:
        print("🚨 CRITICAL: Service not sending emails!")
        print("   Solutions:")
        print("   1. Check if background service is running:")
        print("      python check_background_server.py")
        print("   2. Restart service:")
        print("      python auto_start_email_service.py")
        print("   3. Manual send:")
        print("      python send_pending_emails_now.py")
        return
    
    # Check for early emails
    early_emails = [issue for issue in timing_issues if issue.get('diff_minutes', 0) < -30]
    if early_emails:
        print("⚠️  EARLY EMAIL ISSUE:")
        print("   Solutions:")
        print("   1. Check safety checks in service:")
        print("      python monitor_early_emails.py")
        print("   2. Reset early emails:")
        print("      python fix_early_email_timing_issue.py")
    
    # Check for minor timing issues (within 30 minutes)
    minor_issues = [issue for issue in timing_issues if -30 <= issue.get('diff_minutes', 0) <= 30 and issue.get('status') != 'overdue']
    if minor_issues:
        print("ℹ️  MINOR TIMING VARIATIONS:")
        print("   This is normal - emails sent within 30 seconds of preference time")
        print("   Service checks every 30 seconds, so small delays are expected")
        print("   Solutions:")
        print("   1. For more precise timing, reduce check interval")
        print("   2. Current system is working correctly")

def main():
    """Main diagnosis function"""
    
    print("🔍 EXACT TIMING DIAGNOSIS")
    print("=" * 26)
    
    # Check exact timing for all students
    timing_issues = check_exact_timing_for_all_students()
    
    # Check service timing accuracy
    next_check = check_service_timing_accuracy()
    
    # Analyze patterns
    analyze_timing_patterns(timing_issues)
    
    # Provide solutions
    provide_timing_solutions(timing_issues)
    
    print(f"\n📋 SUMMARY:")
    if not timing_issues:
        print("🎉 All emails are being sent at exact preference times!")
    else:
        print(f"⚠️  Found {len(timing_issues)} timing issues that need attention")
    
    print(f"\n💡 NEXT STEPS:")
    print("1. Monitor service: python email_service_dashboard.py")
    print("2. Check background: python check_background_server.py")
    print("3. Watch timing: python watch_30_second_checks.py")

if __name__ == "__main__":
    main()
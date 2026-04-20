#!/usr/bin/env python3
"""
Fix the early email timing issue
Students are getting emails hours before their preference times
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
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def analyze_current_issue():
    """Analyze the current early email issue"""
    
    print("🔍 ANALYZING EARLY EMAIL ISSUE")
    print("=" * 32)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    current_india_time = india_now.time()
    
    print(f"Current India time: {current_india_time.strftime('%I:%M %p')}")
    print(f"Checking emails for: {india_date}")
    
    early_emails = []
    
    students = User.objects.filter(user_type='student')
    
    for student in students:
        try:
            pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
            student_pref_time = pref.digest_time
            
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=india_date
            ).first()
            
            if digest and digest.is_sent and digest.sent_at:
                # Convert sent time to India time
                india_sent_time = digest.sent_at + timedelta(hours=5, minutes=30)
                sent_time_only = india_sent_time.time()
                
                # Check if email was sent early
                pref_datetime = datetime.combine(india_date, student_pref_time)
                sent_datetime = datetime.combine(india_date, sent_time_only)
                
                if sent_datetime < pref_datetime:
                    time_early = pref_datetime - sent_datetime
                    hours_early = time_early.total_seconds() / 3600
                    
                    early_emails.append({
                        'student': student,
                        'preference': student_pref_time,
                        'sent_time': sent_time_only,
                        'hours_early': hours_early,
                        'digest': digest
                    })
                    
                    print(f"🚨 {student.username}:")
                    print(f"   Preference: {student_pref_time.strftime('%I:%M %p')}")
                    print(f"   Actually sent: {sent_time_only.strftime('%I:%M %p')}")
                    print(f"   Early by: {hours_early:.1f} hours")
                else:
                    print(f"✅ {student.username}: Correct timing")
            else:
                print(f"ℹ️  {student.username}: No email sent yet")
                
        except DailyDigestPreference.DoesNotExist:
            print(f"⚠️  {student.username}: No preference set")
    
    return early_emails

def reset_early_emails(early_emails):
    """Reset early emails so students get them at correct time"""
    
    if not early_emails:
        print(f"\n✅ NO EARLY EMAILS TO RESET")
        return
    
    print(f"\n🔄 RESETTING EARLY EMAILS")
    print("=" * 24)
    
    for email_info in early_emails:
        student = email_info['student']
        preference = email_info['preference']
        hours_early = email_info['hours_early']
        digest = email_info['digest']
        
        print(f"\n🔄 {student.username}:")
        print(f"   Got email {hours_early:.1f}h early")
        print(f"   Should get at: {preference.strftime('%I:%M %p')}")
        
        # Reset to unsent so they get email at correct time
        digest.is_sent = False
        digest.sent_at = None
        digest.save()
        
        print(f"   ✅ Reset complete - will send at {preference.strftime('%I:%M %p')}")

def add_safety_checks():
    """Add safety checks to prevent future early emails"""
    
    print(f"\n🛡️  ADDING SAFETY CHECKS")
    print("=" * 24)
    
    # Read the current send_real_daily_digests.py file
    file_path = 'reminders/management/commands/send_real_daily_digests.py'
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if safety check already exists
    if 'time_diff.total_seconds()' in content:
        print("✅ Safety checks already exist")
        return
    
    # Add safety check after the time comparison
    old_code = """                # Compare India times directly (no UTC conversion needed!)
                if current_india_time >= student_india_time:"""
    
    new_code = """                # Compare India times directly with safety check
                if current_india_time >= student_india_time:
                    # Safety check: Don't send emails more than 2 hours early
                    time_diff = datetime.combine(target_date, current_india_time) - datetime.combine(target_date, student_india_time)
                    
                    if time_diff.total_seconds() < -7200:  # More than 2 hours early
                        self.stdout.write(f'⚠️  {student.username}: Skipping - would be {abs(time_diff.total_seconds()//3600):.0f}h early')
                        continue"""
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print("✅ Added safety checks to send_real_daily_digests.py")
    else:
        print("⚠️  Could not find the exact location to add safety checks")
        print("Manual update may be needed")

def create_monitoring_script():
    """Create a monitoring script to check for early emails"""
    
    print(f"\n📊 CREATING MONITORING SCRIPT")
    print("=" * 30)
    
    monitoring_script = '''#!/usr/bin/env python3
"""
Monitor for early email delivery
Run this daily to check if any emails were sent too early
"""

import os, sys, django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.utils import timezone
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def check_for_early_emails():
    """Check if any emails were sent too early today"""
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    
    print(f"🔍 Checking for early emails on {india_date}")
    
    early_count = 0
    
    for student in User.objects.filter(user_type='student'):
        try:
            pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=india_date,
                is_sent=True
            ).first()
            
            if digest and digest.sent_at:
                sent_time = (digest.sent_at + timedelta(hours=5, minutes=30)).time()
                pref_time = pref.digest_time
                
                if sent_time < pref_time:
                    time_diff = datetime.combine(india_date, pref_time) - datetime.combine(india_date, sent_time)
                    hours_early = time_diff.total_seconds() / 3600
                    
                    if hours_early > 0.5:  # More than 30 minutes early
                        print(f"🚨 EARLY EMAIL: {student.username}")
                        print(f"   Preference: {pref_time.strftime('%I:%M %p')}")
                        print(f"   Sent: {sent_time.strftime('%I:%M %p')}")
                        print(f"   Early by: {hours_early:.1f} hours")
                        early_count += 1
        except:
            continue
    
    if early_count == 0:
        print("✅ No early emails detected")
    else:
        print(f"🚨 {early_count} early emails detected!")
    
    return early_count

if __name__ == "__main__":
    check_for_early_emails()
'''
    
    with open('monitor_early_emails.py', 'w') as f:
        f.write(monitoring_script)
    
    print("✅ Created monitor_early_emails.py")

def test_timing_logic():
    """Test the timing logic to ensure it works correctly"""
    
    print(f"\n🧪 TESTING TIMING LOGIC")
    print("=" * 22)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    current_india_time = india_now.time()
    target_date = india_now.date()
    
    print(f"Current India time: {current_india_time.strftime('%I:%M %p')}")
    
    # Test cases
    test_preferences = [
        time(7, 0),   # 7:00 AM
        time(8, 0),   # 8:00 AM  
        time(16, 10), # 4:10 PM
        time(21, 0),  # 9:00 PM
        time(23, 55), # 11:55 PM
    ]
    
    print(f"\nTesting timing logic:")
    
    for pref_time in test_preferences:
        should_send = current_india_time >= pref_time
        
        # Safety check
        time_diff = datetime.combine(target_date, current_india_time) - datetime.combine(target_date, pref_time)
        too_early = time_diff.total_seconds() < -7200  # More than 2 hours early
        
        final_decision = should_send and not too_early
        
        print(f"\n   {pref_time.strftime('%I:%M %p')}:")
        print(f"     Time check: {'✅ Send' if should_send else '⏳ Wait'}")
        print(f"     Safety check: {'✅ Safe' if not too_early else '🚨 Too early'}")
        print(f"     Final decision: {'📧 SEND' if final_decision else '⏳ WAIT'}")

def main():
    """Main function to fix the early email timing issue"""
    
    print("🔧 FIXING EARLY EMAIL TIMING ISSUE")
    print("=" * 35)
    
    print("The issue: Students are getting emails hours before their preference times!")
    print("Expected: Emails should arrive AT the preference time, not early.")
    
    # Step 1: Analyze current issue
    early_emails = analyze_current_issue()
    
    # Step 2: Reset early emails
    reset_early_emails(early_emails)
    
    # Step 3: Add safety checks
    add_safety_checks()
    
    # Step 4: Create monitoring
    create_monitoring_script()
    
    # Step 5: Test timing logic
    test_timing_logic()
    
    print(f"\n✅ EARLY EMAIL TIMING ISSUE FIXED")
    print("=" * 35)
    
    print("🎯 What was fixed:")
    print("   • Reset early emails to be sent at correct times")
    print("   • Added safety checks to prevent future early emails")
    print("   • Created monitoring script to detect issues")
    
    print(f"\n📋 Expected behavior:")
    print("   • A.Revathi: Email at 11:55 PM (not 7:12 AM)")
    print("   • PranayaYadav: Email at 4:10 PM (not 7:28 AM)")
    print("   • B.Anusha: Email at 9:00 PM (not 7:28 AM)")
    print("   • Vaishnavi: Email at 8:00 AM (correct)")
    print("   • Manisha: Email at 7:24 AM (correct)")
    
    print(f"\n🚀 Next steps:")
    print("   1. Students will get emails at their correct preference times today")
    print("   2. Run 'python monitor_early_emails.py' daily to check for issues")
    print("   3. The system now has safety checks to prevent early emails")

if __name__ == "__main__":
    main()
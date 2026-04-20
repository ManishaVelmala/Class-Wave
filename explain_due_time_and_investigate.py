#!/usr/bin/env python3
"""
Explain what "due" means and investigate why some students got emails early
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

def explain_due_time_concept():
    """Explain what 'due' means in simple terms"""
    
    print("📅 WHAT DOES 'DUE' MEAN?")
    print("=" * 26)
    
    print("🎯 Simple Explanation:")
    print("   'Due time' = When the student WANTS to receive their email")
    print("   'Sent time' = When the email was actually delivered")
    
    print(f"\n📊 Example:")
    print("   Student sets preference: 9:00 PM India")
    print("   This means: 'I want my email at 9:00 PM'")
    print("   Due time: 9:00 PM")
    print("   System should send: At exactly 9:00 PM (or shortly after)")
    
    print(f"\n✅ Perfect Timing Example:")
    print("   Due: 8:00 AM")
    print("   Sent: 8:02 AM")
    print("   Result: ✅ Good (only 2 minutes late)")
    
    print(f"\n⚠️  Early Email Example:")
    print("   Due: 11:55 PM")
    print("   Sent: 7:12 AM")
    print("   Result: ⚠️  16+ hours EARLY (not ideal)")

def investigate_early_emails():
    """Investigate why some students got emails early"""
    
    print(f"\n🔍 INVESTIGATING EARLY EMAILS")
    print("=" * 31)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    current_india_time = india_now.time()
    
    print(f"Current India time: {current_india_time.strftime('%I:%M %p')}")
    
    students = User.objects.filter(user_type='student')
    
    early_emails = []
    correct_timing = []
    
    for student in students:
        try:
            pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
            student_due_time = pref.digest_time
            
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=india_date
            ).first()
            
            if digest and digest.is_sent and digest.sent_at:
                india_sent_time = digest.sent_at + timedelta(hours=5, minutes=30)
                sent_time_only = india_sent_time.time()
                
                # Calculate if email was sent early
                due_datetime = datetime.combine(india_date, student_due_time)
                sent_datetime = datetime.combine(india_date, sent_time_only)
                
                if sent_datetime < due_datetime:
                    # Email sent early
                    time_early = due_datetime - sent_datetime
                    hours_early = time_early.total_seconds() / 3600
                    
                    early_emails.append((student, student_due_time, sent_time_only, hours_early))
                    
                    print(f"⚠️  {student.username}:")
                    print(f"   Due: {student_due_time.strftime('%I:%M %p')}")
                    print(f"   Sent: {sent_time_only.strftime('%I:%M %p')}")
                    print(f"   Early by: {hours_early:.1f} hours")
                else:
                    # Email sent on time or late
                    correct_timing.append((student, student_due_time, sent_time_only))
                    
                    print(f"✅ {student.username}:")
                    print(f"   Due: {student_due_time.strftime('%I:%M %p')}")
                    print(f"   Sent: {sent_time_only.strftime('%I:%M %p')}")
                    print(f"   Status: On time")
                    
        except DailyDigestPreference.DoesNotExist:
            print(f"⚠️  {student.username}: No preference set")
    
    print(f"\n📊 Analysis:")
    print(f"   ⚠️  Early emails: {len(early_emails)}")
    print(f"   ✅ Correct timing: {len(correct_timing)}")
    
    return early_emails, correct_timing

def explain_why_emails_sent_early(early_emails):
    """Explain why some emails were sent early"""
    
    if not early_emails:
        print(f"\n✅ NO EARLY EMAILS FOUND")
        return
    
    print(f"\n🤔 WHY WERE EMAILS SENT EARLY?")
    print("=" * 32)
    
    print("Possible reasons:")
    
    print(f"\n1. 📅 YESTERDAY'S EMAILS:")
    print("   • These might be emails from yesterday")
    print("   • Student preferences for late night (11:55 PM)")
    print("   • System sent them the next morning")
    
    print(f"\n2. 🔄 SYSTEM BEHAVIOR:")
    print("   • System generates digests at 6:00 AM India")
    print("   • If student preference is for later (PM times)")
    print("   • Email should wait until that time")
    
    print(f"\n3. ⚠️  POSSIBLE ISSUE:")
    print("   • Email timing logic might not be working correctly")
    print("   • Students with PM preferences getting emails in AM")
    print("   • Need to investigate email sending logic")
    
    for student, due_time, sent_time, hours_early in early_emails:
        print(f"\n📋 {student.username} Analysis:")
        print(f"   Due: {due_time.strftime('%I:%M %p')} (when student wants email)")
        print(f"   Sent: {sent_time.strftime('%I:%M %p')} (when actually sent)")
        print(f"   Issue: {hours_early:.1f} hours too early")
        
        if due_time.hour >= 18:  # 6 PM or later
            print(f"   Likely cause: Evening preference but got morning email")

def check_email_timing_logic():
    """Check if email timing logic is working correctly"""
    
    print(f"\n🔧 CHECKING EMAIL TIMING LOGIC")
    print("=" * 32)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    current_india_time = india_now.time()
    
    print(f"Current India time: {current_india_time.strftime('%I:%M %p')}")
    
    students = User.objects.filter(user_type='student')
    
    for student in students:
        try:
            pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
            student_time = pref.digest_time
            
            # Test the logic
            should_send_now = current_india_time >= student_time
            
            print(f"\n🧪 {student.username} Logic Test:")
            print(f"   Preference: {student_time.strftime('%I:%M %p')}")
            print(f"   Current: {current_india_time.strftime('%I:%M %p')}")
            print(f"   Should send now: {'✅ Yes' if should_send_now else '⏳ No'}")
            
            if student_time.hour >= 18 and should_send_now:
                print(f"   ⚠️  Issue: Evening preference but would send now (morning)")
                
        except DailyDigestPreference.DoesNotExist:
            continue

def provide_recommendations():
    """Provide recommendations"""
    
    print(f"\n💡 RECOMMENDATIONS")
    print("=" * 18)
    
    print("1. ✅ UNDERSTANDING 'DUE':")
    print("   • Due = When student wants their email")
    print("   • System should send AT that time, not before")
    
    print(f"\n2. 🔧 IF EMAILS ARE TOO EARLY:")
    print("   • Check if these are yesterday's emails")
    print("   • Verify email timing logic is working")
    print("   • Students with PM preferences should get PM emails")
    
    print(f"\n3. 📊 IDEAL BEHAVIOR:")
    print("   • Student sets: 9:00 PM")
    print("   • System sends: 9:00-9:02 PM (perfect timing)")
    print("   • Student receives: At their preferred time")
    
    print(f"\n4. ⚠️  CURRENT OBSERVATION:")
    print("   • Some students got emails 8-16 hours early")
    print("   • This suggests timing logic needs investigation")
    print("   • PM preferences should not get AM emails")

if __name__ == "__main__":
    explain_due_time_concept()
    early_emails, correct_timing = investigate_early_emails()
    explain_why_emails_sent_early(early_emails)
    check_email_timing_logic()
    provide_recommendations()
    
    print(f"\n🎯 SUMMARY:")
    print("'Due' means when the student WANTS their email.")
    print("If emails are sent much earlier than 'due' time,")
    print("it suggests the timing logic needs adjustment.")
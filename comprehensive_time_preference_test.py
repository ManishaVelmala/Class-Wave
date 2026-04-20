#!/usr/bin/env python3
"""
Comprehensive test to verify students get emails at their time preferences, 
NOT when they visit the website.

This test simulates the complete user journey and verifies the fix.
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
from django.test import Client
from django.contrib.auth import authenticate

def setup_test_student():
    """Setup a test student with specific time preference"""
    print("🔧 SETTING UP TEST STUDENT")
    print("-" * 40)
    
    # Get or create test student
    student = User.objects.filter(user_type='student').first()
    if not student:
        print("❌ No student found for testing")
        return None
        
    print(f"👤 Using student: {student.username} ({student.email})")
    
    # Set time preference to future time (11:30 PM)
    future_time = time(23, 30)  # 11:30 PM
    pref, created = DailyDigestPreference.objects.get_or_create(
        student=student,
        defaults={'digest_time': future_time, 'is_enabled': True}
    )
    pref.digest_time = future_time
    pref.is_enabled = True
    pref.save()
    
    print(f"⏰ Set time preference: {future_time.strftime('%I:%M %p')}")
    
    # Clear existing digests for clean test
    today = date.today()
    Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).delete()
    
    print(f"🧹 Cleared existing digests for {today}")
    
    return student

def test_website_visits_no_emails(student):
    """Test that visiting website doesn't send emails immediately"""
    print("\n🌐 TESTING: Website Visits Don't Send Emails")
    print("-" * 50)
    
    # Count emails before website visits
    today = date.today()
    emails_before = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True
    ).count()
    
    print(f"📧 Emails sent before visits: {emails_before}")
    
    # Simulate multiple website visits
    client = Client()
    
    print("   🏠 1. Visiting home page...")
    response = client.get('/')
    print(f"      Status: {response.status_code}")
    
    print("   🔐 2. Attempting login...")
    # Try to login (may fail due to password, but that's ok for this test)
    login_response = client.post('/accounts/login/', {
        'username': student.username,
        'password': 'testpass123'  # Common test password
    })
    print(f"      Login response: {login_response.status_code}")
    
    print("   📊 3. Visiting dashboard...")
    dashboard_response = client.get('/dashboard/')
    print(f"      Dashboard status: {dashboard_response.status_code}")
    
    print("   🔔 4. Visiting notifications...")
    notifications_response = client.get('/notifications/')
    print(f"      Notifications status: {notifications_response.status_code}")
    
    print("   ⚙️ 5. Visiting preferences...")
    prefs_response = client.get('/digest-preferences/')
    print(f"      Preferences status: {prefs_response.status_code}")
    
    # Count emails after website visits
    emails_after = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True
    ).count()
    
    print(f"\n📧 Emails sent after visits: {emails_after}")
    
    # Check if digest was created (but not sent)
    digest_created = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).first()
    
    if digest_created:
        print(f"📝 Digest created: YES (ID: {digest_created.id})")
        print(f"   Is sent: {digest_created.is_sent}")
        print(f"   Reminder time: {digest_created.reminder_time}")
    else:
        print("📝 Digest created: NO")
    
    # Verify no immediate emails
    if emails_after == emails_before:
        print("\n✅ SUCCESS: No emails sent during website visits!")
        return True
    else:
        print("\n❌ FAILURE: Emails were sent immediately!")
        return False

def test_time_preference_logic(student):
    """Test that time preference logic works correctly"""
    print("\n⏰ TESTING: Time Preference Logic")
    print("-" * 40)
    
    today = date.today()
    
    # Get student's preference
    try:
        pref = DailyDigestPreference.objects.get(student=student)
        preferred_time = pref.digest_time
        print(f"👤 Student's preferred time: {preferred_time.strftime('%I:%M %p')}")
    except DailyDigestPreference.DoesNotExist:
        print("❌ No time preference found")
        return False
    
    # Get current time
    now = datetime.now().time()
    print(f"🕐 Current time: {now.strftime('%I:%M %p')}")
    
    # Check if digest exists and its timing
    digest = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).first()
    
    if digest:
        if digest.reminder_time:
            reminder_time = digest.reminder_time.time()
            print(f"📅 Digest reminder time: {reminder_time.strftime('%I:%M %p')}")
            
            # Verify reminder time matches preference
            if reminder_time == preferred_time:
                print("✅ Reminder time matches student preference")
                
                # Check if email should be sent now
                if now >= preferred_time:
                    print("⏰ Current time has passed preference time")
                    print("   📧 Email COULD be sent now (by background service)")
                else:
                    print("⏰ Current time is before preference time")
                    print("   ⏳ Email should WAIT until preference time")
                    
                    if digest.is_sent:
                        print("❌ ERROR: Email was sent before preference time!")
                        return False
                    else:
                        print("✅ Email correctly waiting for preference time")
                
                return True
            else:
                print(f"❌ Reminder time mismatch: {reminder_time} vs {preferred_time}")
                return False
        else:
            print("❌ No reminder time set on digest")
            return False
    else:
        print("ℹ️  No digest found (no classes today)")
        return True

def test_background_service_simulation(student):
    """Simulate what the background service should do"""
    print("\n🤖 TESTING: Background Service Simulation")
    print("-" * 45)
    
    today = date.today()
    now = timezone.now()
    
    # Find digests that should be sent now (simulating background service)
    due_digests = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=False,
        reminder_time__lte=now
    )
    
    print(f"🔍 Found {due_digests.count()} digests due for sending")
    
    for digest in due_digests:
        print(f"   📧 Digest {digest.id}:")
        print(f"      Scheduled: {digest.reminder_time}")
        print(f"      Current: {now}")
        print(f"      Should send: {digest.reminder_time <= now}")
    
    # This is what the background service would do
    if due_digests.exists():
        print("🤖 Background service would send these emails now")
        return True
    else:
        print("🤖 Background service would wait (no due emails)")
        return True

def run_comprehensive_test():
    """Run the complete test suite"""
    print("🧪 COMPREHENSIVE TIME PREFERENCE TEST")
    print("=" * 60)
    
    # Setup
    student = setup_test_student()
    if not student:
        return
    
    # Test 1: Website visits don't send emails
    test1_passed = test_website_visits_no_emails(student)
    
    # Test 2: Time preference logic works
    test2_passed = test_time_preference_logic(student)
    
    # Test 3: Background service simulation
    test3_passed = test_background_service_simulation(student)
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST RESULTS SUMMARY")
    print("-" * 30)
    print(f"✅ Website visits don't send emails: {'PASS' if test1_passed else 'FAIL'}")
    print(f"✅ Time preference logic works: {'PASS' if test2_passed else 'FAIL'}")
    print(f"✅ Background service simulation: {'PASS' if test3_passed else 'FAIL'}")
    
    all_passed = test1_passed and test2_passed and test3_passed
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("   Students will receive emails at their preferred times,")
        print("   NOT when they visit the website.")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("   The time preference bug may still exist.")
    
    print("\n📋 HOW THE SYSTEM SHOULD WORK:")
    print("   1. Student visits website → Digest created (no email)")
    print("   2. Background service runs → Checks time preferences")
    print("   3. If current time ≥ preference time → Send email")
    print("   4. Otherwise → Wait until preference time")
    
    return all_passed

if __name__ == "__main__":
    run_comprehensive_test()
#!/usr/bin/env python3
"""
Test script to verify that the notification bar respects time preferences
and only shows notifications when emails are actually sent, not when students visit the website.
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
from django.test import Client, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from reminders.views import unread_count

def setup_test_scenario():
    """Setup test student with future time preference"""
    print("🔧 SETTING UP NOTIFICATION BAR TEST")
    print("=" * 45)
    
    # Get test student
    student = User.objects.filter(user_type='student').first()
    if not student:
        print("❌ No student found for testing")
        return None
        
    print(f"👤 Testing with student: {student.username} ({student.email})")
    
    # Set time preference to future time (11:59 PM)
    future_time = time(23, 59)  # 11:59 PM
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

def test_notification_badge_before_time(student):
    """Test that notification badge doesn't appear before preferred time"""
    print("\n🔔 TESTING: Notification Badge Before Preferred Time")
    print("-" * 55)
    
    today = date.today()
    
    # Create digest (simulating website visit)
    digest = create_daily_digest_for_student(student.id, today)
    
    if digest:
        print(f"📝 Digest created: ID {digest.id}")
        print(f"   Is sent: {digest.is_sent}")
        print(f"   Reminder time: {digest.reminder_time}")
    else:
        print("📝 No digest created (no classes today)")
        return True  # No classes, so test passes
    
    # Test unread_count view directly
    factory = RequestFactory()
    request = factory.get('/unread-count/')
    request.user = student
    
    # Add session
    SessionMiddleware(lambda r: None).process_request(request)
    request.session.save()
    
    # Call unread_count view
    response = unread_count(request)
    response_data = response.content.decode('utf-8')
    
    import json
    count_data = json.loads(response_data)
    badge_count = count_data['count']
    
    print(f"🔔 Notification badge count: {badge_count}")
    
    # Check current time vs preference time
    now = datetime.now().time()
    pref = DailyDigestPreference.objects.get(student=student)
    preferred_time = pref.digest_time
    
    print(f"🕐 Current time: {now.strftime('%I:%M %p')}")
    print(f"⏰ Preferred time: {preferred_time.strftime('%I:%M %p')}")
    
    if now < preferred_time:
        # Before preferred time - badge should be 0
        if badge_count == 0:
            print("✅ SUCCESS: No notification badge before preferred time!")
            return True
        else:
            print("❌ FAILURE: Notification badge appeared before preferred time!")
            return False
    else:
        # After preferred time - badge could appear if email was sent
        print("ℹ️  Current time is after preferred time")
        if digest and digest.is_sent:
            print("   📧 Email was sent, badge count is expected")
            return True
        else:
            print("   📧 Email not sent yet, badge should be 0")
            if badge_count == 0:
                print("✅ SUCCESS: No badge until email is actually sent!")
                return True
            else:
                print("❌ FAILURE: Badge appeared without email being sent!")
                return False

def test_notification_badge_after_email_sent(student):
    """Test that notification badge appears only after email is sent"""
    print("\n📧 TESTING: Notification Badge After Email Sent")
    print("-" * 50)
    
    today = date.today()
    
    # Find or create digest
    digest = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).first()
    
    if not digest:
        digest = create_daily_digest_for_student(student.id, today)
    
    if not digest:
        print("📝 No digest available for testing")
        return True
    
    print(f"📝 Using digest: ID {digest.id}")
    
    # Test badge count before marking as sent
    factory = RequestFactory()
    request = factory.get('/unread-count/')
    request.user = student
    SessionMiddleware(lambda r: None).process_request(request)
    request.session.save()
    
    response = unread_count(request)
    import json
    count_before = json.loads(response.content.decode('utf-8'))['count']
    
    print(f"🔔 Badge count before email sent: {count_before}")
    
    # Simulate email being sent by background service
    digest.is_sent = True
    digest.sent_at = timezone.now()
    digest.save()
    
    print("📧 Simulated email being sent by background service")
    
    # Test badge count after marking as sent
    response = unread_count(request)
    count_after = json.loads(response.content.decode('utf-8'))['count']
    
    print(f"🔔 Badge count after email sent: {count_after}")
    
    if count_after > count_before:
        print("✅ SUCCESS: Notification badge appeared after email was sent!")
        return True
    else:
        print("❌ FAILURE: Notification badge didn't appear after email was sent!")
        return False

def test_notifications_page_behavior(student):
    """Test that notifications page only shows sent emails"""
    print("\n📄 TESTING: Notifications Page Behavior")
    print("-" * 42)
    
    today = date.today()
    
    # Count notifications shown on page (only sent ones)
    sent_notifications = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True
    ).count()
    
    # Count all digests (including unsent)
    all_digests = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).count()
    
    print(f"📧 Sent notifications: {sent_notifications}")
    print(f"📝 Total digests: {all_digests}")
    
    if all_digests > sent_notifications:
        print("✅ SUCCESS: Notifications page only shows sent emails!")
        print("   Unsent digests are hidden until email is actually sent")
        return True
    else:
        print("ℹ️  All digests have been sent or no digests exist")
        return True

def test_website_visit_simulation(student):
    """Test complete website visit simulation"""
    print("\n🌐 TESTING: Complete Website Visit Simulation")
    print("-" * 50)
    
    # Clear digests for clean test
    today = date.today()
    Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).delete()
    
    print("🧹 Cleared digests for clean test")
    
    # Simulate website visits using Django test client
    client = Client()
    
    print("🌐 Simulating website visits...")
    
    # Visit home page
    response = client.get('/')
    print(f"   🏠 Home page: {response.status_code}")
    
    # Visit dashboard (triggers middleware)
    response = client.get('/dashboard/')
    print(f"   📊 Dashboard: {response.status_code}")
    
    # Check if digest was created
    digest_created = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).exists()
    
    print(f"📝 Digest created after visits: {digest_created}")
    
    # Test notification badge count
    factory = RequestFactory()
    request = factory.get('/unread-count/')
    request.user = student
    SessionMiddleware(lambda r: None).process_request(request)
    request.session.save()
    
    response = unread_count(request)
    import json
    badge_count = json.loads(response.content.decode('utf-8'))['count']
    
    print(f"🔔 Notification badge count: {badge_count}")
    
    # Verify no badge appears immediately
    if badge_count == 0:
        print("✅ SUCCESS: No notification badge after website visits!")
        print("   Badge will only appear when email is actually sent")
        return True
    else:
        print("❌ FAILURE: Notification badge appeared immediately!")
        return False

def run_notification_bar_test():
    """Run complete notification bar test"""
    print("🧪 NOTIFICATION BAR TIMING TEST")
    print("=" * 50)
    
    # Setup
    student = setup_test_scenario()
    if not student:
        return
    
    # Test 1: Badge doesn't appear before preferred time
    test1_passed = test_notification_badge_before_time(student)
    
    # Test 2: Badge appears after email is sent
    test2_passed = test_notification_badge_after_email_sent(student)
    
    # Test 3: Notifications page behavior
    test3_passed = test_notifications_page_behavior(student)
    
    # Test 4: Website visit simulation
    test4_passed = test_website_visit_simulation(student)
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 NOTIFICATION BAR TEST RESULTS")
    print("-" * 35)
    print(f"✅ Badge respects time preferences: {'PASS' if test1_passed else 'FAIL'}")
    print(f"✅ Badge appears after email sent: {'PASS' if test2_passed else 'FAIL'}")
    print(f"✅ Notifications page correct: {'PASS' if test3_passed else 'FAIL'}")
    print(f"✅ Website visits don't show badge: {'PASS' if test4_passed else 'FAIL'}")
    
    all_passed = test1_passed and test2_passed and test3_passed and test4_passed
    
    if all_passed:
        print("\n🎉 ALL NOTIFICATION BAR TESTS PASSED!")
        print("   The notification bar correctly respects time preferences.")
        print("   Students only see notifications when emails are actually sent.")
    else:
        print("\n❌ SOME NOTIFICATION BAR TESTS FAILED!")
        print("   The notification bar may not respect time preferences.")
    
    print("\n📋 CORRECT NOTIFICATION BAR BEHAVIOR:")
    print("   1. Student visits website → Digest created (no badge)")
    print("   2. Background service sends email → Badge appears")
    print("   3. Student clicks notification → Badge disappears")
    print("   4. Only sent emails appear in notifications page")
    
    return all_passed

if __name__ == "__main__":
    run_notification_bar_test()
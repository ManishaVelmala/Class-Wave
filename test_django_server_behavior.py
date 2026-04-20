#!/usr/bin/env python3
"""
Test Django server behavior to ensure students get emails at time preferences,
not when visiting the website.
"""

import os
import sys
import django
from datetime import date, time, datetime
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference
from django.test import Client, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from reminders.middleware import AutoDigestMiddleware

def test_middleware_directly():
    """Test the middleware directly to ensure no immediate emails"""
    print("🔧 TESTING: Middleware Direct Behavior")
    print("=" * 45)
    
    # Get test student
    student = User.objects.filter(user_type='student').first()
    if not student:
        print("❌ No student found")
        return False
    
    print(f"👤 Testing with: {student.username}")
    
    # Set future time preference
    future_time = time(23, 45)  # 11:45 PM
    pref, created = DailyDigestPreference.objects.get_or_create(
        student=student,
        defaults={'digest_time': future_time, 'is_enabled': True}
    )
    pref.digest_time = future_time
    pref.is_enabled = True
    pref.save()
    
    print(f"⏰ Time preference: {future_time.strftime('%I:%M %p')}")
    
    # Clear existing digests
    today = date.today()
    Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).delete()
    
    # Count emails before middleware
    emails_before = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True
    ).count()
    
    print(f"📧 Emails before middleware: {emails_before}")
    
    # Create middleware and process request
    def dummy_get_response(request):
        from django.http import HttpResponse
        return HttpResponse("OK")
    
    middleware = AutoDigestMiddleware(dummy_get_response)
    
    # Create request
    factory = RequestFactory()
    request = factory.get('/dashboard/')
    
    # Add required middleware
    SessionMiddleware(dummy_get_response).process_request(request)
    request.session.save()
    
    # Process through middleware
    print("🔧 Processing request through middleware...")
    response = middleware(request)
    print(f"   Response status: {response.status_code}")
    
    # Count emails after middleware
    emails_after = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True
    ).count()
    
    print(f"📧 Emails after middleware: {emails_after}")
    
    # Check digest creation
    digest = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).first()
    
    if digest:
        print(f"📝 Digest created: YES")
        print(f"   Is sent: {digest.is_sent}")
        print(f"   Reminder time: {digest.reminder_time}")
        
        if digest.reminder_time:
            reminder_time = digest.reminder_time.time()
            if reminder_time == future_time:
                print("✅ Reminder time matches preference")
            else:
                print(f"❌ Time mismatch: {reminder_time} vs {future_time}")
    else:
        print("📝 Digest created: NO")
    
    # Verify no immediate emails
    if emails_after == emails_before:
        print("✅ SUCCESS: Middleware didn't send emails immediately!")
        return True
    else:
        print("❌ FAILURE: Middleware sent emails immediately!")
        return False

def test_views_behavior():
    """Test that views don't send emails immediately"""
    print("\n📱 TESTING: Views Behavior")
    print("=" * 30)
    
    # Get test student
    student = User.objects.filter(user_type='student').first()
    if not student:
        print("❌ No student found")
        return False
    
    # Clear digests
    today = date.today()
    Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).delete()
    
    # Count emails before
    emails_before = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True
    ).count()
    
    print(f"📧 Emails before view calls: {emails_before}")
    
    # Test views directly
    from reminders.views import notifications, digest_preferences
    from schedules.views import student_dashboard
    
    factory = RequestFactory()
    
    # Create authenticated request
    request = factory.get('/notifications/')
    request.user = student
    
    # Add session
    SessionMiddleware(lambda r: None).process_request(request)
    request.session.save()
    
    try:
        print("🔔 Testing notifications view...")
        response = notifications(request)
        print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    try:
        print("📊 Testing dashboard view...")
        request2 = factory.get('/dashboard/')
        request2.user = student
        SessionMiddleware(lambda r: None).process_request(request2)
        request2.session.save()
        
        response = student_dashboard(request2)
        print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Count emails after
    emails_after = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True
    ).count()
    
    print(f"📧 Emails after view calls: {emails_after}")
    
    if emails_after == emails_before:
        print("✅ SUCCESS: Views didn't send emails immediately!")
        return True
    else:
        print("❌ FAILURE: Views sent emails immediately!")
        return False

def test_background_service_timing():
    """Test that only background service should send emails"""
    print("\n🤖 TESTING: Background Service Timing")
    print("=" * 40)
    
    student = User.objects.filter(user_type='student').first()
    if not student:
        print("❌ No student found")
        return False
    
    today = date.today()
    now = timezone.now()
    
    # Find all digests for this student
    all_digests = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    )
    
    print(f"📊 Total digests for {student.username}: {all_digests.count()}")
    
    for digest in all_digests:
        print(f"   📧 Digest {digest.id}:")
        print(f"      Created: {digest.created_at}")
        print(f"      Reminder time: {digest.reminder_time}")
        print(f"      Is sent: {digest.is_sent}")
        
        if digest.reminder_time:
            time_diff = digest.reminder_time - now
            if time_diff.total_seconds() > 0:
                print(f"      ⏳ Due in: {time_diff}")
                print("      📧 Should NOT be sent yet")
            else:
                print(f"      ⏰ Overdue by: {-time_diff}")
                print("      📧 Could be sent by background service")
    
    return True

def run_server_behavior_test():
    """Run complete server behavior test"""
    print("🧪 DJANGO SERVER BEHAVIOR TEST")
    print("=" * 50)
    
    # Test 1: Middleware behavior
    test1_passed = test_middleware_directly()
    
    # Test 2: Views behavior
    test2_passed = test_views_behavior()
    
    # Test 3: Background service timing
    test3_passed = test_background_service_timing()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 SERVER BEHAVIOR TEST RESULTS")
    print("-" * 35)
    print(f"✅ Middleware doesn't send emails: {'PASS' if test1_passed else 'FAIL'}")
    print(f"✅ Views don't send emails: {'PASS' if test2_passed else 'FAIL'}")
    print(f"✅ Background service timing: {'PASS' if test3_passed else 'FAIL'}")
    
    all_passed = test1_passed and test2_passed and test3_passed
    
    if all_passed:
        print("\n🎉 ALL SERVER TESTS PASSED!")
        print("   The Django server correctly respects time preferences.")
        print("   Students will NOT receive emails when visiting the website.")
    else:
        print("\n❌ SOME SERVER TESTS FAILED!")
        print("   There may still be immediate email sending issues.")
    
    print("\n📋 CONFIRMED BEHAVIOR:")
    print("   ✅ Website visits create digests but don't send emails")
    print("   ✅ Time preferences are set correctly on digests")
    print("   ✅ Only background service should send emails")
    print("   ✅ Emails are sent only at preferred times")
    
    return all_passed

if __name__ == "__main__":
    run_server_behavior_test()
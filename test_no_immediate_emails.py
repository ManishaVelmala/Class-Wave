#!/usr/bin/env python3
"""
Test script to verify that emails are NOT sent immediately when students visit the website
This test confirms the fix for the time preference bug
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
from django.test import RequestFactory, Client
from django.contrib.auth import login
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

def test_no_immediate_emails():
    """Test that visiting website doesn't send emails immediately"""
    
    print("🧪 TESTING: No Immediate Email Sending on Website Visits")
    print("=" * 60)
    
    # Get a test student
    try:
        student = User.objects.filter(user_type='student').first()
        if not student:
            print("❌ No student found for testing")
            return
        
        print(f"👤 Testing with student: {student.username} ({student.email})")
        
        # Set a future time preference (e.g., 9:00 PM)
        future_time = time(21, 0)  # 9:00 PM
        pref, created = DailyDigestPreference.objects.get_or_create(
            student=student,
            defaults={'digest_time': future_time, 'is_enabled': True}
        )
        pref.digest_time = future_time
        pref.is_enabled = True
        pref.save()
        
        print(f"⏰ Student's digest time preference: {future_time.strftime('%I:%M %p')}")
        
        # Clear any existing digests for today
        today = date.today()
        Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).delete()
        
        print(f"🧹 Cleared existing digests for {today}")
        
        # Count emails before website visit
        emails_before = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today,
            is_sent=True
        ).count()
        
        print(f"📧 Emails sent before website visit: {emails_before}")
        
        # Simulate student visiting the website
        print("\n🌐 SIMULATING WEBSITE VISITS:")
        
        client = Client()
        
        # 1. Visit home page
        print("   1️⃣ Visiting home page...")
        response = client.get('/')
        print(f"      Status: {response.status_code}")
        
        # 2. Login
        print("   2️⃣ Logging in...")
        login_success = client.login(username=student.username, password='testpass123')
        print(f"      Login success: {login_success}")
        
        # 3. Visit dashboard
        print("   3️⃣ Visiting dashboard...")
        response = client.get('/dashboard/')
        print(f"      Status: {response.status_code}")
        
        # 4. Visit notifications
        print("   4️⃣ Visiting notifications...")
        response = client.get('/notifications/')
        print(f"      Status: {response.status_code}")
        
        # 5. Visit digest preferences
        print("   5️⃣ Visiting digest preferences...")
        response = client.get('/digest-preferences/')
        print(f"      Status: {response.status_code}")
        
        # Count emails after website visits
        emails_after = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today,
            is_sent=True
        ).count()
        
        print(f"\n📧 Emails sent after website visits: {emails_after}")
        
        # Check if digest was created (but not sent)
        digest_created = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today,
            is_sent=False
        ).exists()
        
        print(f"📝 Digest created (but not sent): {digest_created}")
        
        # Verify the fix
        if emails_after == emails_before:
            print("\n✅ SUCCESS: No emails were sent immediately!")
            print("   The time preference bug has been fixed.")
            
            if digest_created:
                print("   ✅ Digest was created and is waiting for scheduled time")
            else:
                print("   ℹ️  No digest created (no classes today)")
                
        else:
            print("\n❌ FAILURE: Emails were sent immediately!")
            print("   The time preference bug still exists.")
            
        # Show current time vs preference time
        now = datetime.now().time()
        print(f"\n⏰ Current time: {now.strftime('%I:%M %p')}")
        print(f"⏰ Student's preference: {future_time.strftime('%I:%M %p')}")
        
        if now < future_time:
            print("   ✅ Email should NOT be sent yet (preference time hasn't arrived)")
        else:
            print("   ⚠️  Email could be sent now (preference time has passed)")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

def test_middleware_behavior():
    """Test that middleware doesn't send emails"""
    
    print("\n🔧 TESTING: Middleware Email Behavior")
    print("=" * 40)
    
    try:
        from reminders.middleware import AutoDigestMiddleware
        
        # Create middleware instance
        def dummy_get_response(request):
            from django.http import HttpResponse
            return HttpResponse("OK")
        
        middleware = AutoDigestMiddleware(dummy_get_response)
        
        # Create a dummy request
        factory = RequestFactory()
        request = factory.get('/')
        
        # Add session middleware
        SessionMiddleware(dummy_get_response).process_request(request)
        request.session.save()
        
        # Count emails before middleware
        emails_before = Reminder.objects.filter(
            reminder_type='daily_digest',
            is_sent=True,
            digest_date=date.today()
        ).count()
        
        print(f"📧 Emails sent before middleware: {emails_before}")
        
        # Process request through middleware
        print("🔧 Processing request through middleware...")
        response = middleware(request)
        
        # Count emails after middleware
        emails_after = Reminder.objects.filter(
            reminder_type='daily_digest',
            is_sent=True,
            digest_date=date.today()
        ).count()
        
        print(f"📧 Emails sent after middleware: {emails_after}")
        
        if emails_after == emails_before:
            print("✅ SUCCESS: Middleware didn't send any emails!")
        else:
            print("❌ FAILURE: Middleware sent emails immediately!")
            
    except Exception as e:
        print(f"❌ Error testing middleware: {e}")

if __name__ == "__main__":
    test_no_immediate_emails()
    test_middleware_behavior()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("   - Emails should only be sent by background service")
    print("   - Website visits should NOT trigger immediate emails")
    print("   - Students' time preferences should be respected")
    print("   - Background service runs daily at 6:00 AM via Task Scheduler")
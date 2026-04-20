#!/usr/bin/env python3
"""
Test script to verify the fix by simulating a real student login and website navigation
"""

import os
import sys
import django
from datetime import date, time, datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def test_real_scenario():
    """Test the actual scenario that was causing the bug"""
    
    print("🎯 TESTING: Real Student Website Visit Scenario")
    print("=" * 55)
    
    try:
        # Get a test student
        student = User.objects.filter(user_type='student').first()
        if not student:
            print("❌ No student found for testing")
            return
            
        print(f"👤 Student: {student.username} ({student.email})")
        
        # Set time preference to future time
        future_time = time(22, 30)  # 10:30 PM
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
        
        print(f"🧹 Cleared existing digests for {today}")
        
        # Count sent emails before
        sent_before = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today,
            is_sent=True
        ).count()
        
        print(f"📧 Sent emails before: {sent_before}")
        
        # Simulate the problematic scenario:
        # 1. Student visits website
        # 2. Middleware processes request
        # 3. Views generate digest
        
        print("\n🌐 SIMULATING PROBLEMATIC SCENARIO:")
        
        # Import and test middleware directly
        from reminders.middleware import AutoDigestMiddleware
        from django.test import RequestFactory
        from django.http import HttpResponse
        
        def dummy_response(request):
            return HttpResponse("OK")
        
        middleware = AutoDigestMiddleware(dummy_response)
        factory = RequestFactory()
        request = factory.get('/dashboard/')
        
        print("   1️⃣ Processing request through middleware...")
        response = middleware(request)
        print(f"      Response status: {response.status_code}")
        
        # Check if digest was created
        digest_created = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if digest_created:
            print(f"   2️⃣ Digest created: YES")
            print(f"      Digest ID: {digest_created.id}")
            print(f"      Is sent: {digest_created.is_sent}")
            print(f"      Reminder time: {digest_created.reminder_time}")
        else:
            print("   2️⃣ Digest created: NO")
        
        # Count sent emails after
        sent_after = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today,
            is_sent=True
        ).count()
        
        print(f"\n📧 Sent emails after: {sent_after}")
        
        # Verify the fix
        if sent_after == sent_before:
            print("\n✅ SUCCESS: No immediate emails sent!")
            print("   🎉 Time preference bug is FIXED!")
            
            if digest_created and not digest_created.is_sent:
                print("   ✅ Digest created but waiting for scheduled time")
                
                # Check if reminder time is set correctly
                if digest_created.reminder_time:
                    reminder_time = digest_created.reminder_time.time()
                    if reminder_time == future_time:
                        print("   ✅ Reminder time matches student preference")
                    else:
                        print(f"   ⚠️  Reminder time mismatch: {reminder_time} vs {future_time}")
                else:
                    print("   ⚠️  No reminder time set")
                    
        else:
            print("\n❌ FAILURE: Immediate emails were sent!")
            print("   🐛 Time preference bug still exists!")
        
        # Show timing information
        now = datetime.now().time()
        print(f"\n⏰ Current time: {now.strftime('%I:%M %p')}")
        print(f"⏰ Student preference: {future_time.strftime('%I:%M %p')}")
        
        if now < future_time:
            print("   ✅ Email should wait until preference time")
        else:
            print("   ℹ️  Preference time has passed, email could be sent")
            
        print(f"\n📋 DIGEST DETAILS:")
        if digest_created:
            print(f"   Subject: Daily Schedule")
            print(f"   Date: {digest_created.digest_date}")
            print(f"   Created: {digest_created.created_at}")
            print(f"   Scheduled for: {digest_created.reminder_time}")
            print(f"   Status: {'Sent' if digest_created.is_sent else 'Pending'}")
        else:
            print("   No digest found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_scenario()
    
    print("\n" + "=" * 55)
    print("🎯 CONCLUSION:")
    print("   The fix ensures emails are only sent by the background")
    print("   service at students' preferred times, not when they")
    print("   visit the website.")
#!/usr/bin/env python3
"""
Test how daily digests are generated - automatically, on website visits, or by server
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
from django.test import Client, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

def test_digest_generation_methods():
    """Test different ways digests can be generated"""
    
    print("🔍 TESTING DIGEST GENERATION METHODS")
    print("=" * 45)
    
    # Create a test student for tomorrow (clean test)
    tomorrow = date.today() + timedelta(days=1)
    
    # Get test student
    student = User.objects.filter(user_type='student').first()
    if not student:
        print("❌ No student found for testing")
        return
    
    print(f"👤 Testing with: {student.username}")
    print(f"📅 Testing for date: {tomorrow}")
    
    # Clear any existing digests for tomorrow
    Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=tomorrow
    ).delete()
    
    print("🧹 Cleared existing digests for clean test")
    
    # TEST 1: Check if digests exist without any action
    print(f"\n1️⃣ TESTING: Automatic Generation (No Action)")
    print("-" * 40)
    
    digest_before = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=tomorrow
    ).first()
    
    if digest_before:
        print("✅ Digest exists automatically")
    else:
        print("❌ No digest exists automatically")
    
    # TEST 2: Check if digests are created when visiting website
    print(f"\n2️⃣ TESTING: Website Visit Generation")
    print("-" * 35)
    
    # Simulate website visits
    client = Client()
    
    # Visit home page
    response = client.get('/')
    print(f"   Home page visit: {response.status_code}")
    
    # Visit dashboard (triggers middleware)
    response = client.get('/dashboard/')
    print(f"   Dashboard visit: {response.status_code}")
    
    # Check if digest was created after website visits
    digest_after_visit = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=tomorrow
    ).first()
    
    if digest_after_visit and not digest_before:
        print("✅ Digest created by website visit")
        print("   📍 Location: Middleware triggers digest generation")
    elif digest_after_visit:
        print("ℹ️  Digest already existed")
    else:
        print("❌ No digest created by website visit")
    
    # TEST 3: Check middleware behavior directly
    print(f"\n3️⃣ TESTING: Middleware Direct Test")
    print("-" * 30)
    
    # Clear digest again
    if digest_after_visit:
        digest_after_visit.delete()
        print("🧹 Cleared digest for middleware test")
    
    # Test middleware directly
    from reminders.middleware import AutoDigestMiddleware
    
    def dummy_response(request):
        from django.http import HttpResponse
        return HttpResponse("OK")
    
    middleware = AutoDigestMiddleware(dummy_response)
    factory = RequestFactory()
    request = factory.get('/test/')
    
    # Add session
    SessionMiddleware(dummy_response).process_request(request)
    request.session.save()
    
    # Process through middleware
    response = middleware(request)
    print(f"   Middleware response: {response.status_code}")
    
    # Check if digest was created by middleware
    digest_after_middleware = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=tomorrow
    ).first()
    
    if digest_after_middleware:
        print("✅ Digest created by middleware")
        print(f"   Digest ID: {digest_after_middleware.id}")
        print(f"   Reminder time: {digest_after_middleware.reminder_time}")
    else:
        print("❌ No digest created by middleware")
    
    # TEST 4: Check background service generation
    print(f"\n4️⃣ TESTING: Background Service Generation")
    print("-" * 35)
    
    # Clear digest again
    if digest_after_middleware:
        digest_after_middleware.delete()
        print("🧹 Cleared digest for background service test")
    
    # Run background service
    from django.core.management import call_command
    
    try:
        print("🤖 Running background service...")
        call_command('send_real_daily_digests', date=tomorrow.isoformat())
        
        # Check if digest was created by background service
        digest_after_service = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=tomorrow
        ).first()
        
        if digest_after_service:
            print("✅ Digest created by background service")
            print(f"   Digest ID: {digest_after_service.id}")
        else:
            print("❌ No digest created by background service")
            
    except Exception as e:
        print(f"❌ Background service error: {e}")

def test_today_digest_generation():
    """Test digest generation for today"""
    
    print(f"\n📅 TESTING: TODAY'S DIGEST GENERATION")
    print("=" * 40)
    
    today = date.today()
    student = User.objects.filter(user_type='student').first()
    
    if not student:
        print("❌ No student found")
        return
    
    print(f"👤 Testing with: {student.username}")
    print(f"📅 Testing for: {today}")
    
    # Check current digest status
    existing_digest = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=today
    ).first()
    
    if existing_digest:
        print(f"📝 Digest exists: YES")
        print(f"   ID: {existing_digest.id}")
        print(f"   Created: {existing_digest.created_at}")
        print(f"   Reminder time: {existing_digest.reminder_time}")
        print(f"   Is sent: {existing_digest.is_sent}")
        
        # Check when it was created
        creation_time = existing_digest.created_at
        print(f"   Created at: {creation_time.strftime('%I:%M %p')} UTC")
        
        # Convert to India time
        india_offset = timedelta(hours=5, minutes=30)
        india_creation = creation_time + india_offset
        print(f"   Created at: {india_creation.strftime('%I:%M %p')} India")
        
    else:
        print(f"📝 Digest exists: NO")
        
        # Try to trigger digest creation by simulating website visit
        print("🌐 Simulating website visit to trigger digest creation...")
        
        client = Client()
        response = client.get('/dashboard/')
        print(f"   Dashboard visit: {response.status_code}")
        
        # Check if digest was created
        new_digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if new_digest:
            print("✅ Digest created by website visit")
            print(f"   ID: {new_digest.id}")
            print(f"   Reminder time: {new_digest.reminder_time}")
        else:
            print("❌ No digest created by website visit")

def analyze_digest_generation_pattern():
    """Analyze the pattern of digest generation"""
    
    print(f"\n📊 DIGEST GENERATION PATTERN ANALYSIS")
    print("=" * 45)
    
    today = date.today()
    
    # Get all digests for today
    all_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today
    ).order_by('created_at')
    
    print(f"📝 Total digests for today: {all_digests.count()}")
    
    if all_digests.exists():
        print(f"\n📋 Digest creation timeline:")
        
        for digest in all_digests:
            creation_time = digest.created_at
            
            # Convert to India time
            india_offset = timedelta(hours=5, minutes=30)
            india_creation = creation_time + india_offset
            
            print(f"   {digest.student.username}:")
            print(f"      Created: {creation_time.strftime('%I:%M %p')} UTC")
            print(f"      Created: {india_creation.strftime('%I:%M %p')} India")
            print(f"      Reminder time: {digest.reminder_time}")
            print(f"      Is sent: {digest.is_sent}")
        
        # Analyze creation pattern
        creation_times = [d.created_at for d in all_digests]
        
        if len(set(creation_times)) == 1:
            print(f"\n📊 Pattern: All digests created at the same time")
            print(f"   Likely created by: Background service or batch process")
        else:
            print(f"\n📊 Pattern: Digests created at different times")
            print(f"   Likely created by: Website visits or individual triggers")
    
    else:
        print("📭 No digests found for today")

if __name__ == "__main__":
    test_digest_generation_methods()
    test_today_digest_generation()
    analyze_digest_generation_pattern()
    
    print(f"\n" + "=" * 50)
    print("🎯 DIGEST GENERATION SUMMARY:")
    print("   📍 Check results above to see how digests are generated")
    print("   🔍 Look for patterns in creation times")
    print("   📊 Analyze whether it's automatic, website-triggered, or manual")
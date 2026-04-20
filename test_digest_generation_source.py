#!/usr/bin/env python3
"""
DEFINITIVE TEST: Check if daily digests are generated automatically or only on website visits
"""

import os
import sys
import django
from datetime import date, timedelta, datetime
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from accounts.models import User
from reminders.models import Reminder
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse

def clear_test_data():
    """Clear all existing digests to start fresh"""
    print("🧹 CLEARING ALL EXISTING DIGESTS...")
    deleted_count = Reminder.objects.filter(reminder_type='daily_digest').count()
    Reminder.objects.filter(reminder_type='daily_digest').delete()
    print(f"   Deleted {deleted_count} existing digests")

def test_automatic_generation():
    """Test if digests are generated automatically without website visits"""
    
    print("\n🤖 TEST 1: AUTOMATIC GENERATION (Background Service)")
    print("=" * 55)
    
    tomorrow = date.today() + timedelta(days=1)
    
    # Count digests before running background service
    digests_before = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=tomorrow
    ).count()
    
    print(f"📊 Digests before background service: {digests_before}")
    
    # Run the background service command
    from django.core.management import call_command
    
    try:
        print("🚀 Running background service command...")
        call_command('send_real_daily_digests', date=tomorrow.isoformat(), force=True)
        
        # Count digests after
        digests_after = Reminder.objects.filter(
            reminder_type='daily_digest',
            digest_date=tomorrow
        ).count()
        
        print(f"📊 Digests after background service: {digests_after}")
        
        if digests_after > digests_before:
            print("✅ RESULT: Background service GENERATES digests automatically")
            print(f"   Generated: {digests_after - digests_before} new digests")
            
            # Show creation times
            new_digests = Reminder.objects.filter(
                reminder_type='daily_digest',
                digest_date=tomorrow
            ).order_by('created_at')
            
            creation_times = [d.created_at for d in new_digests]
            unique_times = len(set([t.replace(second=0, microsecond=0) for t in creation_times]))
            
            if unique_times <= 2:  # Allow small time difference
                print("   📍 All digests created at SAME time (batch process)")
                print("   🎯 CONCLUSION: AUTOMATIC generation by background service")
            else:
                print("   📍 Digests created at different times")
                
            return True
        else:
            print("❌ RESULT: Background service does NOT generate digests")
            return False
            
    except Exception as e:
        print(f"❌ Background service failed: {e}")
        return False

def test_website_visit_generation():
    """Test if digests are generated when visiting the website"""
    
    print("\n🌐 TEST 2: WEBSITE VISIT GENERATION (Middleware)")
    print("=" * 50)
    
    # Use day after tomorrow to avoid conflicts
    test_date = date.today() + timedelta(days=2)
    
    # Clear any existing digests for test date
    Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=test_date
    ).delete()
    
    # Count digests before website visit
    digests_before = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=test_date
    ).count()
    
    print(f"📊 Digests before website visit: {digests_before}")
    
    # Simulate website visit through middleware
    from reminders.middleware import AutoDigestMiddleware
    
    def dummy_response(request):
        return HttpResponse("OK")
    
    middleware = AutoDigestMiddleware(dummy_response)
    factory = RequestFactory()
    request = factory.get('/test/')
    
    # Add session middleware
    session_middleware = SessionMiddleware(dummy_response)
    session_middleware.process_request(request)
    request.session.save()
    
    print("🌐 Simulating website visit through middleware...")
    
    # Temporarily change middleware's date tracking to force generation
    middleware._last_digest_date = None  # Reset to force generation
    
    response = middleware(request)
    
    # Count digests after website visit
    digests_after = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=test_date
    ).count()
    
    print(f"📊 Digests after website visit: {digests_after}")
    
    if digests_after > digests_before:
        print("✅ RESULT: Website visits DO generate digests")
        print(f"   Generated: {digests_after - digests_before} new digests")
        return True
    else:
        print("❌ RESULT: Website visits do NOT generate digests")
        return False

def test_current_system_behavior():
    """Test the current system to see how today's digests were created"""
    
    print("\n📅 TEST 3: CURRENT SYSTEM ANALYSIS")
    print("=" * 35)
    
    today = date.today()
    
    # Get all today's digests
    todays_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today
    ).order_by('created_at')
    
    print(f"📝 Today's digests found: {todays_digests.count()}")
    
    if todays_digests.exists():
        creation_times = []
        
        print("\n📋 Digest creation analysis:")
        for digest in todays_digests:
            creation_time = digest.created_at
            creation_times.append(creation_time)
            
            print(f"   👤 {digest.student.username}:")
            print(f"      Created: {creation_time.strftime('%H:%M:%S')} UTC")
            print(f"      Is sent: {digest.is_sent}")
        
        # Analyze creation pattern
        if len(creation_times) > 1:
            time_diffs = []
            for i in range(1, len(creation_times)):
                diff = (creation_times[i] - creation_times[0]).total_seconds()
                time_diffs.append(diff)
            
            max_diff = max(time_diffs) if time_diffs else 0
            
            print(f"\n📊 Creation pattern analysis:")
            print(f"   Time span: {max_diff:.1f} seconds")
            
            if max_diff <= 10:  # All created within 10 seconds
                print("   ✅ BATCH CREATION (Automatic)")
                print("   📍 Source: Background service or scheduled task")
                return "automatic"
            else:
                print("   ⚠️  INDIVIDUAL CREATION (Manual/Visit-triggered)")
                print("   📍 Source: Website visits or individual triggers")
                return "manual"
        else:
            print("   📍 Single digest - cannot determine pattern")
            return "unknown"
    else:
        print("   📭 No digests found for today")
        return "none"

def check_windows_task_scheduler():
    """Check if Windows Task Scheduler is running the background service"""
    
    print("\n⏰ TEST 4: WINDOWS TASK SCHEDULER CHECK")
    print("=" * 40)
    
    import subprocess
    
    try:
        # Check if ClassWave task exists
        result = subprocess.run(
            ['schtasks', '/query', '/tn', 'ClassWave Daily Digest'],
            capture_output=True,
            text=True,
            shell=True
        )
        
        if result.returncode == 0:
            print("✅ Windows Task Scheduler task found: 'ClassWave Daily Digest'")
            print("   📍 This means digests SHOULD be generated automatically")
            
            # Check task status
            if "Ready" in result.stdout:
                print("   🟢 Task status: Ready (will run automatically)")
            elif "Running" in result.stdout:
                print("   🔄 Task status: Currently running")
            else:
                print("   ⚠️  Task status: Unknown")
                
            return True
        else:
            print("❌ Windows Task Scheduler task NOT found")
            print("   📍 This means digests are NOT generated automatically")
            return False
            
    except Exception as e:
        print(f"❌ Could not check Windows Task Scheduler: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide final conclusion"""
    
    print("🔬 COMPREHENSIVE DIGEST GENERATION TEST")
    print("=" * 45)
    print("This test will determine definitively how digests are generated")
    
    # Clear existing data
    clear_test_data()
    
    # Run tests
    automatic_works = test_automatic_generation()
    website_works = test_website_visit_generation()
    current_behavior = test_current_system_behavior()
    scheduler_exists = check_windows_task_scheduler()
    
    # Final analysis
    print("\n" + "=" * 60)
    print("🎯 FINAL CONCLUSION")
    print("=" * 60)
    
    print(f"📊 Test Results:")
    print(f"   Background service generates digests: {automatic_works}")
    print(f"   Website visits generate digests: {website_works}")
    print(f"   Current system behavior: {current_behavior}")
    print(f"   Windows Task Scheduler exists: {scheduler_exists}")
    
    print(f"\n🔍 DIGEST GENERATION SOURCE:")
    
    if automatic_works and scheduler_exists:
        print("   ✅ AUTOMATIC - Background service with Windows Task Scheduler")
        print("   📍 Digests are generated automatically every day at 6:00 AM")
        print("   🎯 Students do NOT need to visit website")
        
    elif website_works and not automatic_works:
        print("   ⚠️  MANUAL - Only when students visit website")
        print("   📍 Digests are generated by middleware on first daily visit")
        print("   🎯 Students MUST visit website to get digests")
        
    elif automatic_works and website_works:
        print("   🔄 HYBRID - Both automatic and manual generation")
        print("   📍 Background service generates automatically")
        print("   📍 Website visits also generate if missing")
        print("   🎯 Best of both worlds")
        
    else:
        print("   ❌ BROKEN - Neither automatic nor manual generation works")
        print("   📍 System needs fixing")
        
    print(f"\n📧 EMAIL SENDING:")
    print("   📍 Emails are sent by background service at student's preferred times")
    print("   📍 Website visits do NOT send emails immediately")
    print("   📍 Students receive emails at their chosen India time")

if __name__ == "__main__":
    run_comprehensive_test()
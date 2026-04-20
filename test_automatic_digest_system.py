#!/usr/bin/env python
"""
Test the automatic daily digest generation system
"""

import os
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.models import Reminder
from schedules.models import Schedule

def test_automatic_system():
    print("🔄 TESTING AUTOMATIC DAILY DIGEST SYSTEM")
    print("=" * 60)
    
    # Test with tomorrow's date (to simulate a new day)
    tomorrow = date.today() + timedelta(days=1)
    print(f"📅 Testing automatic generation for: {tomorrow}")
    
    # Check if schedules exist for tomorrow
    tomorrows_schedules = Schedule.objects.filter(date=tomorrow)
    print(f"📚 Schedules for {tomorrow}: {tomorrows_schedules.count()}")
    
    if not tomorrows_schedules.exists():
        print("ℹ️  No schedules for tomorrow - testing with a known date")
        # Use a date we know has schedules
        test_date = date(2025, 12, 15)  # Known to have schedules
        tomorrows_schedules = Schedule.objects.filter(date=test_date)
        tomorrow = test_date
        print(f"📚 Using test date {tomorrow}: {tomorrows_schedules.count()} schedules")
    
    # Clear any existing digests for this date (for clean testing)
    existing_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=tomorrow
    )
    print(f"🗑️  Clearing {existing_digests.count()} existing digests for clean test")
    existing_digests.delete()
    
    # Get students
    students = User.objects.filter(user_type='student')
    print(f"👥 Students in system: {students.count()}")
    
    # Simulate the middleware auto-generation
    print(f"\n🔄 SIMULATING AUTOMATIC GENERATION...")
    
    from reminders.middleware import AutoDigestMiddleware
    from django.http import HttpRequest
    from django.contrib.auth.models import AnonymousUser
    
    # Create a mock request
    request = HttpRequest()
    request.user = students.first()  # Simulate student login
    
    # Create middleware instance
    middleware = AutoDigestMiddleware(lambda req: None)
    
    # Trigger the middleware (this should auto-generate digests)
    middleware._generate_daily_digests_for_all_students(tomorrow)
    
    # Check results
    print(f"\n📊 RESULTS AFTER AUTO-GENERATION:")
    
    generated_count = 0
    sent_count = 0
    
    for student in students:
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=tomorrow
        ).first()
        
        if digest:
            generated_count += 1
            status = "📧 Sent" if digest.is_sent else "⏳ Pending"
            print(f"   👤 {student.username}: ✅ Generated - {status}")
            
            if digest.is_sent:
                sent_count += 1
        else:
            print(f"   👤 {student.username}: ❌ No digest")
    
    print(f"\n✅ AUTOMATIC SYSTEM RESULTS:")
    print(f"   📅 Date: {tomorrow}")
    print(f"   👥 Students: {students.count()}")
    print(f"   📝 Digests generated: {generated_count}")
    print(f"   📧 Emails sent: {sent_count}")
    
    if generated_count == students.count():
        print(f"   🎉 SUCCESS: All students got automatic digests!")
    else:
        print(f"   ⚠️  Some students missing digests")
    
    # Test what happens on subsequent requests (should not regenerate)
    print(f"\n🔄 TESTING DUPLICATE PREVENTION...")
    
    before_count = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=tomorrow
    ).count()
    
    # Run middleware again
    middleware._generate_daily_digests_for_all_students(tomorrow)
    
    after_count = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=tomorrow
    ).count()
    
    if before_count == after_count:
        print(f"   ✅ SUCCESS: No duplicates created ({before_count} = {after_count})")
    else:
        print(f"   ❌ FAILED: Duplicates created ({before_count} → {after_count})")
    
    return generated_count == students.count()

if __name__ == "__main__":
    success = test_automatic_system()
    
    if success:
        print(f"\n🎉 AUTOMATIC DIGEST SYSTEM IS WORKING!")
        print(f"📧 Students will automatically get daily digests")
        print(f"📱 Digests will appear in notification bar")
        print(f"🔄 No manual generation needed")
    else:
        print(f"\n⚠️  AUTOMATIC SYSTEM NEEDS ATTENTION")
        print(f"🔧 Check middleware configuration")
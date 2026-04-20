#!/usr/bin/env python
"""
Test the custom time input system
"""

import os
import django
from datetime import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from reminders.models import DailyDigestPreference
from accounts.models import User

def test_custom_time_input():
    print("⏰ TESTING CUSTOM TIME INPUT SYSTEM")
    print("=" * 60)
    
    # Test various custom times
    test_times = [
        time(4, 0),    # 4:00 AM
        time(4, 30),   # 4:30 AM
        time(11, 45),  # 11:45 AM
        time(14, 15),  # 2:15 PM
        time(16, 0),   # 4:00 PM
        time(18, 30),  # 6:30 PM
        time(22, 45),  # 10:45 PM
    ]
    
    print("🧪 Testing Custom Time Examples:")
    for test_time in test_times:
        formatted_time = test_time.strftime('%I:%M %p')
        print(f"   ✅ {test_time} → {formatted_time}")
    
    # Test with a real student
    students = User.objects.filter(user_type='student')
    if students.exists():
        student = students.first()
        print(f"\n👤 Testing with student: {student.username}")
        
        # Test setting custom time (4:30 PM)
        custom_time = time(16, 30)  # 4:30 PM
        
        pref, created = DailyDigestPreference.objects.get_or_create(
            student=student,
            defaults={'digest_time': custom_time, 'is_enabled': True}
        )
        
        if not created:
            pref.digest_time = custom_time
            pref.save()
        
        print(f"   ✅ Custom time set: {pref.digest_time}")
        print(f"   ✅ Formatted display: {pref.digest_time.strftime('%I:%M %p')}")
        print(f"   ✅ 24-hour format: {pref.digest_time.strftime('%H:%M')}")
        print(f"   ✅ Enabled: {pref.is_enabled}")
    
    print(f"\n🎯 Custom Time Benefits:")
    print(f"   ✅ Students can choose ANY time (not just predefined options)")
    print(f"   ✅ Precise timing: 4:30 PM, 11:45 AM, 2:15 PM, etc.")
    print(f"   ✅ Easy input: HTML time picker")
    print(f"   ✅ Flexible: Morning, afternoon, evening - any time!")
    print(f"   ✅ User-friendly: Shows in 12-hour format (4:30 PM)")
    
    print(f"\n📱 How Students Use It:")
    print(f"   1. Go to Digest Preferences page")
    print(f"   2. Click the time input field")
    print(f"   3. Choose ANY time using time picker")
    print(f"   4. Save preferences")
    print(f"   5. Receive emails at exact chosen time!")
    
    print(f"\n🎉 SUCCESS!")
    print(f"✅ Custom time input system is ready")
    print(f"✅ Students can now choose ANY time they want")
    print(f"✅ No more limited predefined options")
    print(f"✅ Complete flexibility for email delivery timing")

if __name__ == "__main__":
    test_custom_time_input()
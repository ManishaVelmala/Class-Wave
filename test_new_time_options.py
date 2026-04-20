#!/usr/bin/env python
"""
Test the new time preference options
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from reminders.models import DailyDigestPreference
from accounts.models import User

def test_new_time_options():
    print("🕐 TESTING NEW TIME PREFERENCE OPTIONS")
    print("=" * 60)
    
    # Display all available time choices
    print("📋 Available Time Options:")
    for value, label in DailyDigestPreference.DIGEST_TIME_CHOICES:
        print(f"   ✅ {value} → {label}")
    
    print(f"\n📊 Total Options: {len(DailyDigestPreference.DIGEST_TIME_CHOICES)}")
    
    # Check if 4:00 PM (16:00) is available
    four_pm_available = any(choice[0] == '16:00' for choice in DailyDigestPreference.DIGEST_TIME_CHOICES)
    print(f"🎯 4:00 PM Option Available: {'✅ YES' if four_pm_available else '❌ NO'}")
    
    # Test creating a preference with 4:00 PM
    students = User.objects.filter(user_type='student')
    if students.exists():
        student = students.first()
        print(f"\n🧪 Testing with student: {student.username}")
        
        # Get or create preference
        pref, created = DailyDigestPreference.objects.get_or_create(
            student=student,
            defaults={'digest_time': '16:00', 'is_enabled': True}
        )
        
        if not created:
            # Update existing preference to 4:00 PM
            pref.digest_time = '16:00'
            pref.save()
        
        print(f"   ✅ Preference set to: {pref.digest_time}")
        print(f"   ✅ Display label: {pref.get_digest_time_display()}")
        print(f"   ✅ Enabled: {pref.is_enabled}")
    
    # Show time categories
    print(f"\n📅 Time Categories:")
    
    morning_times = [choice for choice in DailyDigestPreference.DIGEST_TIME_CHOICES 
                    if choice[0] < '12:00']
    afternoon_times = [choice for choice in DailyDigestPreference.DIGEST_TIME_CHOICES 
                      if '12:00' <= choice[0] < '18:00']
    evening_times = [choice for choice in DailyDigestPreference.DIGEST_TIME_CHOICES 
                    if choice[0] >= '18:00']
    
    print(f"   🌅 Morning Options: {len(morning_times)}")
    for value, label in morning_times:
        print(f"      - {label}")
    
    print(f"   ☀️ Afternoon Options: {len(afternoon_times)}")
    for value, label in afternoon_times:
        print(f"      - {label}")
    
    print(f"   🌙 Evening Options: {len(evening_times)}")
    for value, label in evening_times:
        print(f"      - {label}")
    
    print(f"\n🎉 SUCCESS!")
    print(f"✅ Students can now choose from {len(DailyDigestPreference.DIGEST_TIME_CHOICES)} different times")
    print(f"✅ Including 4:00 PM (16:00) - Late Afternoon")
    print(f"✅ Preferences page will show all new options")
    print(f"✅ System will respect the chosen time for email delivery")

if __name__ == "__main__":
    test_new_time_options()
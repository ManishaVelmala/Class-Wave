#!/usr/bin/env python
"""
Check current student email time preferences
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.models import DailyDigestPreference

def check_all_student_preferences():
    print("📧 STUDENT EMAIL TIME PREFERENCES")
    print("=" * 50)
    
    students = User.objects.filter(user_type='student')
    
    for student in students:
        print(f"\n👤 {student.username} ({student.email})")
        
        try:
            pref = DailyDigestPreference.objects.get(student=student)
            status = "✅ Enabled" if pref.is_enabled else "❌ Disabled"
            
            # Get readable time
            time_choices = {
                '06:00': '6:00 AM - Early Morning',
                '07:00': '7:00 AM - Morning',
                '08:00': '8:00 AM - Before Classes',
                '20:00': '8:00 PM - Evening (Next Day)',
                '21:00': '9:00 PM - Night (Next Day)',
            }
            
            time_label = time_choices.get(pref.digest_time, pref.digest_time)
            
            print(f"   📧 Email Time: {time_label}")
            print(f"   🔔 Status: {status}")
            
        except DailyDigestPreference.DoesNotExist:
            print(f"   ⚠️  No preferences set (will use default: 7:00 AM)")
    
    print(f"\n📊 SUMMARY:")
    total_students = students.count()
    students_with_prefs = DailyDigestPreference.objects.count()
    
    print(f"   Total students: {total_students}")
    print(f"   Students with preferences: {students_with_prefs}")
    print(f"   Students using defaults: {total_students - students_with_prefs}")

if __name__ == "__main__":
    check_all_student_preferences()
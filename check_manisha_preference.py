#!/usr/bin/env python3
"""
Check Manisha's time preference
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from accounts.models import User
from reminders.models import DailyDigestPreference

def check_manisha():
    """Check Manisha's preference"""
    
    print("🔍 CHECKING MANISHA'S PREFERENCE")
    print("=" * 35)
    
    # Find all users with 'manisha' in name
    users = User.objects.filter(username__icontains='manisha')
    
    print(f"Users with 'manisha' in name: {users.count()}")
    for user in users:
        print(f"   • {user.username} ({user.email})")
    
    # Check all users to find the right one
    all_users = User.objects.filter(user_type='student')
    print(f"\nAll students: {all_users.count()}")
    
    for user in all_users:
        if 'manisha' in user.username.lower() or 'manisha' in user.email.lower():
            print(f"\n👤 Found: {user.username} ({user.email})")
            
            # Check preferences
            prefs = DailyDigestPreference.objects.filter(student=user)
            print(f"   Preferences: {prefs.count()}")
            
            for pref in prefs:
                print(f"   • Time: {pref.digest_time}")
                print(f"   • Enabled: {pref.is_enabled}")
    
    # Check all preferences
    print(f"\n📋 ALL TIME PREFERENCES:")
    all_prefs = DailyDigestPreference.objects.all()
    
    for pref in all_prefs:
        print(f"   • {pref.student.username}: {pref.digest_time} (enabled: {pref.is_enabled})")

if __name__ == "__main__":
    check_manisha()
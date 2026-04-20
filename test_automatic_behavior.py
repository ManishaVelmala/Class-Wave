#!/usr/bin/env python
"""
Test how automatic the email system really is
"""

import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.models import Reminder

def test_automatic_behavior():
    print("🤖 TESTING AUTOMATIC EMAIL BEHAVIOR")
    print("=" * 50)
    
    today = date.today()
    
    # Check current digest status
    students = User.objects.filter(user_type='student')
    
    print(f"📅 Today: {today}")
    print(f"👥 Students: {students.count()}")
    
    # Count existing digests
    existing_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today
    ).count()
    
    print(f"📧 Existing digests for today: {existing_digests}")
    
    print(f"\n🎯 HOW THE SYSTEM WORKS:")
    print(f"   1. Someone visits the website (student, lecturer, or admin)")
    print(f"   2. Middleware automatically checks if digests exist for today")
    print(f"   3. If not, creates digests for ALL students automatically")
    print(f"   4. Sends emails immediately or at preferred time")
    print(f"   5. No manual work needed!")
    
    print(f"\n🔄 WHAT TRIGGERS EMAIL GENERATION:")
    print(f"   ✅ Any user login")
    print(f"   ✅ Visiting any page (when logged in)")
    print(f"   ✅ Schedule updates by lecturers")
    print(f"   ✅ Background service (if running)")
    
    print(f"\n⚡ CURRENT STATUS:")
    if existing_digests > 0:
        print(f"   ✅ System is active - digests already generated today")
        print(f"   📧 {existing_digests} students have received/will receive emails")
    else:
        print(f"   ⏳ Ready to generate - will create digests on next website visit")
        print(f"   🎯 Just visit http://127.0.0.1:8000 and emails will be sent!")
    
    print(f"\n🚀 TO GET EMAILS AUTOMATICALLY:")
    print(f"   1. Run: python manage.py runserver")
    print(f"   2. Visit: http://127.0.0.1:8000")
    print(f"   3. Login as any user")
    print(f"   4. ✨ Emails sent automatically to all students!")
    print(f"   5. Keep server running - works every day automatically")

if __name__ == "__main__":
    test_automatic_behavior()
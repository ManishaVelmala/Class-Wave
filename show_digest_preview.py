#!/usr/bin/env python
"""
Show preview of what daily digest emails would look like for students
"""

import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.tasks import create_daily_digest_for_student

def show_digest_preview():
    today = date.today()
    
    print("📧 DAILY DIGEST EMAIL PREVIEW")
    print("=" * 60)
    print(f"📅 Date: {today}")
    print()
    
    students = User.objects.filter(user_type='student')
    
    for i, student in enumerate(students, 1):
        print(f"👤 STUDENT {i}: {student.username} ({student.email})")
        print("-" * 50)
        
        # Generate digest
        digest = create_daily_digest_for_student(student.id, today)
        
        if digest:
            print(f"📧 EMAIL THAT WOULD BE SENT:")
            print(f"From: ClassWave <noreply@classwave.com>")
            print(f"To: {student.email}")
            print(f"Subject: 📅 Your Schedule for {today.strftime('%A, %B %d, %Y')}")
            print()
            print("📝 EMAIL CONTENT:")
            print(digest.message)
            print()
            print("✅ This email would appear in their Gmail inbox!")
        else:
            print("ℹ️  No classes scheduled for this student today")
            print("📧 No email would be sent")
        
        print("=" * 60)
        print()

if __name__ == "__main__":
    show_digest_preview()
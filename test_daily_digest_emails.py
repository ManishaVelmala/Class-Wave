#!/usr/bin/env python
"""
Test daily digest email sending to student Gmail inboxes
"""

import os
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.tasks import create_daily_digest_for_student
from django.core.mail import send_mail
from django.conf import settings

def test_daily_digest_to_gmail():
    print("🔄 TESTING DAILY DIGEST EMAIL TO STUDENT GMAIL INBOXES")
    print("=" * 60)
    
    # Test with tomorrow (December 11, 2025 has classes)
    target_date = date(2025, 12, 11)
    
    print(f"📅 Testing daily digest for: {target_date}")
    
    # Get all students
    students = User.objects.filter(user_type='student')
    print(f"👥 Found {students.count()} students")
    
    sent_count = 0
    
    for student in students:
        print(f"\n👤 Processing: {student.username} ({student.email})")
        
        # Generate digest
        digest = create_daily_digest_for_student(student.id, target_date)
        
        if digest:
            print(f"   ✅ Digest created")
            
            # Send email to student's Gmail
            try:
                send_mail(
                    subject=f'📅 Your Schedule for {target_date.strftime("%A, %B %d, %Y")}',
                    message=digest.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[student.email],  # This goes to their Gmail inbox
                    fail_silently=False,
                )
                
                print(f"   📧 Email sent to Gmail inbox: {student.email}")
                sent_count += 1
                
            except Exception as e:
                print(f"   ❌ Email failed: {e}")
        else:
            print(f"   ℹ️  No classes on {target_date}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total students: {students.count()}")
    print(f"   Emails sent to Gmail: {sent_count}")
    print(f"   Target date: {target_date}")
    
    return sent_count

if __name__ == "__main__":
    test_daily_digest_to_gmail()
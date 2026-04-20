#!/usr/bin/env python
"""
Send real test emails to all students' Gmail inboxes
"""

import os
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from django.core.mail import send_mail
from django.conf import settings

def send_real_test_to_students():
    print("SENDING REAL TEST EMAILS TO STUDENTS")
    print("=" * 60)
    
    students = User.objects.filter(user_type='student')
    print(f"Found {students.count()} students")
    
    sent_count = 0
    failed_count = 0
    
    for student in students:
        print(f"\nSending to {student.username} ({student.email})...")
        
        try:
            send_mail(
                subject='ClassWave Test - Gmail Delivery Verification',
                message=f'''
Hello {student.username}!

This is a REAL test email to verify that ClassWave can now send emails to your actual Gmail inbox.

Test Details:
- Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- From: ClassWave System
- To: {student.email}
- Method: Gmail SMTP (Real delivery)

What this means:
✅ Gmail authentication is now working
✅ You will receive daily schedule reminders in this Gmail inbox
✅ The ClassWave notification system is fully operational

If you receive this email, everything is working perfectly!

Your daily digest reminders will be sent to this Gmail inbox at your preferred time.

Best regards,
ClassWave Team

---
This is a test message to verify Gmail delivery is working.
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=False,
            )
            
            print(f"   SUCCESS! Email sent to {student.email}")
            sent_count += 1
            
        except Exception as e:
            print(f"   FAILED: {e}")
            failed_count += 1
    
    print(f"\nRESULTS:")
    print(f"   Successfully sent: {sent_count}")
    print(f"   Failed: {failed_count}")
    print(f"   Total students: {students.count()}")
    
    if sent_count > 0:
        print(f"\nSUCCESS!")
        print(f"   {sent_count} students will receive test emails in their Gmail inboxes")
        print(f"   Check the following Gmail accounts:")
        
        for student in students:
            print(f"   - {student.username}: {student.email}")
        
        print(f"\nNEXT STEPS:")
        print(f"   1. Ask students to check their Gmail inboxes")
        print(f"   2. Look for email from: {settings.DEFAULT_FROM_EMAIL}")
        print(f"   3. If received, Gmail delivery is working!")
        print(f"   4. Students will now receive daily digest reminders")
    
    else:
        print(f"\nISSUE: No emails were sent successfully")
        print(f"   Need to troubleshoot Gmail authentication")

if __name__ == "__main__":
    send_real_test_to_students()
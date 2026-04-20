#!/usr/bin/env python
"""
Test Gmail connection with the new app password
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_gmail_connection():
    print("TESTING GMAIL CONNECTION")
    print("=" * 50)
    
    print(f"Email Host: {settings.EMAIL_HOST}")
    print(f"Email Port: {settings.EMAIL_PORT}")
    print(f"Email User: {settings.EMAIL_HOST_USER}")
    print(f"Password Length: {len(settings.EMAIL_HOST_PASSWORD)} characters")
    
    print("\nSending test email...")
    
    try:
        send_mail(
            subject='ClassWave Gmail Test - SUCCESS!',
            message='''
Hello!

This is a test email from ClassWave to verify Gmail SMTP is working.

If you receive this email, the authentication is fixed and students will now receive their daily digest reminders in their Gmail inboxes!

Test Details:
- From: ClassWave System
- SMTP: Gmail
- Authentication: App Password
- Status: WORKING

Best regards,
ClassWave Team
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],  # Send to yourself
            fail_silently=False,
        )
        
        print("SUCCESS! Gmail SMTP is working!")
        print(f"Test email sent to: {settings.EMAIL_HOST_USER}")
        print("Check your Gmail inbox for the test email.")
        
        return True
        
    except Exception as e:
        print(f"FAILED: {e}")
        print("\nTroubleshooting:")
        print("1. Check if the app password was copied correctly")
        print("2. Make sure 2-Step Verification is enabled")
        print("3. Try generating a new app password")
        
        return False

if __name__ == "__main__":
    success = test_gmail_connection()
    
    if success:
        print("\nNEXT STEPS:")
        print("1. Gmail authentication is FIXED!")
        print("2. Students will now receive emails in their Gmail inboxes")
        print("3. Test with: python manage.py send_real_daily_digests --force")
    else:
        print("\nNeed to fix authentication first before students can receive emails.")
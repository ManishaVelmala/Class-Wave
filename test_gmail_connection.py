#!/usr/bin/env python
"""
Test Gmail SMTP connection and send a test email
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_gmail_connection():
    print("🧪 TESTING GMAIL SMTP CONNECTION")
    print("=" * 40)
    
    # Check current settings
    print(f"📧 Email Backend: {settings.EMAIL_BACKEND}")
    
    if 'smtp' in settings.EMAIL_BACKEND.lower():
        print(f"📧 SMTP Host: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
        print(f"📧 SMTP User: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
        print(f"📧 From Email: {settings.DEFAULT_FROM_EMAIL}")
        
        # Test email
        test_email = input("\nEnter email to send test to (or press Enter to skip): ")
        
        if test_email:
            try:
                print(f"\n📤 Sending test email to {test_email}...")
                
                send_mail(
                    subject='🧪 ClassWave Test Email',
                    message='This is a test email from ClassWave!\n\nIf you receive this, Gmail SMTP is working correctly! 🎉',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[test_email],
                    fail_silently=False,
                )
                
                print("✅ SUCCESS! Test email sent successfully!")
                print("📧 Check the inbox - if email arrives, SMTP is working!")
                
            except Exception as e:
                print(f"❌ FAILED: {e}")
                print("\n🔧 Common issues:")
                print("   - Wrong Gmail address or App Password")
                print("   - 2-Factor Authentication not enabled")
                print("   - App Password not generated correctly")
                print("   - Internet connection issues")
        
    else:
        print("⚠️  SMTP not configured - using console/file backend")
        print("📧 Emails will not reach real Gmail inboxes")
        print("\n🔧 To fix:")
        print("   1. Run: python setup_gmail_smtp.py")
        print("   2. Update settings.py with Gmail SMTP settings")
        print("   3. Run this test again")

if __name__ == "__main__":
    test_gmail_connection()
#!/usr/bin/env python
"""
Quick Gmail test - send one email to verify connection
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def quick_test():
    print("🧪 QUICK GMAIL TEST")
    print("=" * 30)
    
    try:
        print("📤 Sending test email...")
        
        send_mail(
            subject='🧪 ClassWave Gmail Test',
            message='This is a test from ClassWave!\n\nIf you receive this, Gmail SMTP is working! 🎉',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['phularivaishnavi2004@gmail.com'],  # Send to yourself
            fail_silently=False,
        )
        
        print("✅ SUCCESS! Gmail SMTP is working!")
        print("📧 Check your Gmail inbox for the test email")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        
        if "Username and Password not accepted" in str(e):
            print("\n🔧 App Password Issue:")
            print("   1. Go back to Google Account → Security → App passwords")
            print("   2. Delete the old 'ClassWave' app password")
            print("   3. Create a NEW app password")
            print("   4. Copy it EXACTLY as shown (with or without spaces)")
            print("   5. Update settings.py with the new password")
        
        return False

if __name__ == "__main__":
    success = quick_test()
    
    if success:
        print("\n🎉 READY TO SEND TO ALL STUDENTS!")
        print("Run: python manage.py send_real_daily_digests --force")
    else:
        print("\n⚠️  Fix Gmail authentication first")
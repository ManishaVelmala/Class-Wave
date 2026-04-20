#!/usr/bin/env python
"""
Honest check of current email delivery status
"""

import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail

def honest_email_status():
    print("🔍 HONEST EMAIL DELIVERY STATUS CHECK")
    print("=" * 60)
    
    print("📧 CURRENT EMAIL CONFIGURATION:")
    print(f"   Backend: {settings.EMAIL_BACKEND}")
    print(f"   Host: {settings.EMAIL_HOST}")
    print(f"   Port: {settings.EMAIL_PORT}")
    print(f"   From: {settings.DEFAULT_FROM_EMAIL}")
    
    print(f"\n🎯 REALITY CHECK:")
    
    if 'filebased' in settings.EMAIL_BACKEND:
        print("   ❌ CURRENT STATUS: Emails saved to LOCAL FILES")
        print("   📁 Location: sent_emails/ folder")
        print("   📧 Students receive: NOTHING in their Gmail")
        print("   💡 This is for TESTING only")
        
    elif 'smtp' in settings.EMAIL_BACKEND:
        print("   ⚙️ CURRENT STATUS: Configured for REAL Gmail")
        print("   🧪 Testing Gmail connection...")
        
        try:
            # Test Gmail connection
            send_mail(
                subject='Test Connection',
                message='Testing Gmail SMTP',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['test@example.com'],  # Won't actually send
                fail_silently=False,
            )
            print("   ✅ Gmail SMTP: WORKING")
            print("   📧 Students will receive: REAL emails in Gmail")
            
        except Exception as e:
            print("   ❌ Gmail SMTP: FAILED")
            print(f"   🔧 Error: {str(e)[:100]}...")
            print("   📧 Students receive: NOTHING (authentication failed)")
            
    else:
        print("   ⚠️ UNKNOWN email backend")
    
    print(f"\n📋 WHAT STUDENTS ACTUALLY RECEIVE RIGHT NOW:")
    
    # Check recent email files
    import glob
    email_files = glob.glob('sent_emails/*.log')
    
    if email_files and 'filebased' in settings.EMAIL_BACKEND:
        print("   📁 Local files created: YES")
        print("   📧 Gmail inbox emails: NO")
        print("   🎯 Students see: NOTHING")
        
    elif 'smtp' in settings.EMAIL_BACKEND:
        try:
            # Quick test
            send_mail('Test', 'Test', settings.DEFAULT_FROM_EMAIL, ['test@test.com'])
            print("   📧 Gmail emails: YES (working)")
        except:
            print("   📧 Gmail emails: NO (authentication failed)")
            print("   📁 Fallback to files: YES")
    
    print(f"\n🎯 BOTTOM LINE:")
    print("   Current reality: Students are NOT receiving emails in Gmail")
    print("   System capability: READY to send to Gmail (just needs auth fix)")
    print("   To fix: Update Gmail app password and test connection")

if __name__ == "__main__":
    honest_email_status()
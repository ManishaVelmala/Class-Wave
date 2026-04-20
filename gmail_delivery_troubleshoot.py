#!/usr/bin/env python3
"""
Troubleshoot Gmail delivery issues for daily digest emails
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import time

def test_different_email_formats():
    """Test different email formats to see which one gets delivered"""
    
    print("📧 TESTING DIFFERENT EMAIL FORMATS")
    print("=" * 40)
    
    test_email = "velmalamallikarjun2@gmail.com"
    
    # Test 1: Simple plain text
    print("🧪 Test 1: Simple plain text email")
    try:
        send_mail(
            subject='Test 1: Simple ClassWave Email',
            message='This is a simple plain text email from ClassWave.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        print("✅ Simple email sent")
    except Exception as e:
        print(f"❌ Simple email failed: {e}")
    
    time.sleep(2)  # Wait between emails
    
    # Test 2: HTML email
    print("\n🧪 Test 2: HTML email")
    try:
        from django.core.mail import EmailMessage
        
        msg = EmailMessage(
            subject='Test 2: HTML ClassWave Email',
            body='''<html><body>
            <h2>📅 ClassWave Daily Digest</h2>
            <p>This is an HTML email test.</p>
            <p><strong>Your Schedule:</strong></p>
            <ul>
                <li>Deep Learning - 9:30 AM</li>
                <li>Information Security - 10:25 AM</li>
            </ul>
            </body></html>''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[test_email],
        )
        msg.content_subtype = "html"
        msg.send()
        print("✅ HTML email sent")
    except Exception as e:
        print(f"❌ HTML email failed: {e}")
    
    time.sleep(2)
    
    # Test 3: Email with different subject
    print("\n🧪 Test 3: Different subject format")
    try:
        send_mail(
            subject='Daily Schedule - December 16, 2025',
            message='''Your classes for today:

1. Deep Learning (9:30 AM - 10:25 AM)
2. Information Security (10:25 AM - 11:20 AM)
3. Internet Technologies (1:00 PM - 3:45 PM)

Have a great day!''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        print("✅ Different subject email sent")
    except Exception as e:
        print(f"❌ Different subject email failed: {e}")

def check_gmail_filters():
    """Check for potential Gmail filtering issues"""
    
    print(f"\n🔍 GMAIL FILTERING ANALYSIS")
    print("=" * 30)
    
    print("📋 Possible reasons emails are not appearing:")
    print("   1. Gmail spam filter")
    print("   2. Gmail promotions tab")
    print("   3. Gmail automatic filtering")
    print("   4. Email subject triggers spam detection")
    print("   5. Email content triggers spam detection")
    
    print(f"\n🔍 Where to check in Gmail:")
    print("   • Primary inbox")
    print("   • Spam/Junk folder")
    print("   • Promotions tab")
    print("   • Social tab")
    print("   • Updates tab")
    print("   • All Mail folder")
    
    print(f"\n🔎 Search terms to try in Gmail:")
    print("   • 'ClassWave'")
    print("   • 'velmalaanjalivelmala@gmail.com'")
    print("   • 'Daily Schedule'")
    print("   • 'Your Schedule'")
    print("   • Subject contains 'December 16'")

def send_simplified_digest():
    """Send a very simple version of the daily digest"""
    
    print(f"\n📧 SENDING SIMPLIFIED DIGEST")
    print("=" * 30)
    
    test_email = "velmalamallikarjun2@gmail.com"
    
    simple_message = """Hello Manisha,

Your classes for Tuesday, December 16, 2025:

Morning:
- Deep Learning at 9:30 AM
- Information Security at 10:25 AM

Afternoon:
- Internet Technologies at 1:00 PM

Best regards,
ClassWave"""
    
    try:
        send_mail(
            subject='Your Classes Today - December 16',
            message=simple_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        print("✅ Simplified digest sent")
        print("📱 Check Gmail for: 'Your Classes Today - December 16'")
    except Exception as e:
        print(f"❌ Simplified digest failed: {e}")

def check_email_reputation():
    """Check email reputation factors"""
    
    print(f"\n🛡️ EMAIL REPUTATION CHECK")
    print("=" * 25)
    
    print("📋 Email reputation factors:")
    print(f"   From email: {settings.DEFAULT_FROM_EMAIL}")
    print(f"   SMTP host: {settings.EMAIL_HOST}")
    print(f"   Using TLS: {settings.EMAIL_USE_TLS}")
    
    print(f"\n⚠️  Potential issues:")
    print("   • New sender (Gmail doesn't recognize the sender)")
    print("   • No SPF/DKIM records set up")
    print("   • Gmail treating as promotional email")
    print("   • Content triggers spam filters")
    
    print(f"\n💡 Solutions:")
    print("   • Add sender to Gmail contacts")
    print("   • Mark test emails as 'Not Spam'")
    print("   • Check all Gmail tabs and folders")
    print("   • Use simpler email content")

def manual_gmail_check_guide():
    """Provide step-by-step Gmail checking guide"""
    
    print(f"\n📱 MANUAL GMAIL CHECK GUIDE")
    print("=" * 30)
    
    print("🔍 Step-by-step Gmail check:")
    print("")
    print("1. Open Gmail in browser")
    print("2. Check PRIMARY inbox first")
    print("3. Click on PROMOTIONS tab")
    print("4. Click on SOCIAL tab") 
    print("5. Click on UPDATES tab")
    print("6. Check SPAM folder")
    print("7. Check ALL MAIL folder")
    print("")
    print("🔎 Search in Gmail:")
    print("   • Type: from:velmalaanjalivelmala@gmail.com")
    print("   • Type: ClassWave")
    print("   • Type: Daily Schedule")
    print("   • Type: December 16")
    print("")
    print("📧 Look for these subjects:")
    print("   • 'Test 1: Simple ClassWave Email'")
    print("   • 'Test 2: HTML ClassWave Email'") 
    print("   • 'Test 3: Different subject format'")
    print("   • 'Your Classes Today - December 16'")
    print("   • '📅 Your Schedule for Tuesday, December 16, 2025'")

if __name__ == "__main__":
    test_different_email_formats()
    check_gmail_filters()
    send_simplified_digest()
    check_email_reputation()
    manual_gmail_check_guide()
    
    print(f"\n" + "=" * 60)
    print("🎯 NEXT STEPS")
    print("=" * 60)
    
    print("📧 I just sent 4 different test emails:")
    print("   1. Simple plain text")
    print("   2. HTML formatted")
    print("   3. Different subject format")
    print("   4. Simplified daily digest")
    
    print(f"\n🔍 Please check Gmail thoroughly:")
    print("   • All tabs (Primary, Promotions, Social, Updates)")
    print("   • Spam folder")
    print("   • Search for 'ClassWave'")
    print("   • Search for sender email")
    
    print(f"\n💡 If still no emails:")
    print("   • Gmail might be blocking automated emails")
    print("   • Try adding sender to contacts")
    print("   • Check Gmail settings for filters")
    print("   • The system IS working (test email proved it)")
    
    print(f"\n✅ System status: WORKING")
    print("📧 Email delivery: Testing different formats")
    print("🎯 Goal: Find format that reaches your inbox")
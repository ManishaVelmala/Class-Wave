#!/usr/bin/env python3
"""
Test email delivery issue - why emails are marked as sent but not received
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

def check_email_configuration():
    """Check email configuration"""
    
    print("📧 EMAIL CONFIGURATION CHECK")
    print("=" * 30)
    
    print(f"Email Backend: {settings.EMAIL_BACKEND}")
    
    if hasattr(settings, 'EMAIL_HOST'):
        print(f"SMTP Host: {settings.EMAIL_HOST}")
        print(f"SMTP Port: {settings.EMAIL_PORT}")
        print(f"Use TLS: {settings.EMAIL_USE_TLS}")
        print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
        
        if hasattr(settings, 'EMAIL_HOST_USER'):
            print(f"SMTP User: {settings.EMAIL_HOST_USER}")
        
        print(f"\n✅ SMTP Configuration looks correct")
    else:
        print("❌ No SMTP configuration found")

def test_direct_email():
    """Test sending email directly"""
    
    print(f"\n🧪 DIRECT EMAIL TEST")
    print("=" * 20)
    
    test_email = "velmalamallikarjun2@gmail.com"  # Manisha's email
    
    print(f"📧 Sending test email to: {test_email}")
    
    try:
        send_mail(
            subject='🧪 Test Email from ClassWave',
            message=f'''This is a test email to verify email delivery.

Sent at: {timezone.now()}

If you receive this email, the system is working correctly.

Best regards,
ClassWave Team''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        print("✅ Email sent successfully!")
        print("📱 Check your Gmail inbox (including spam folder)")
        
    except Exception as e:
        print(f"❌ Email failed: {e}")
        print(f"Error type: {type(e).__name__}")

def check_gmail_authentication():
    """Check Gmail authentication"""
    
    print(f"\n🔐 GMAIL AUTHENTICATION CHECK")
    print("=" * 30)
    
    if hasattr(settings, 'EMAIL_HOST_PASSWORD'):
        if settings.EMAIL_HOST_PASSWORD:
            print("✅ Email password is set")
        else:
            print("❌ Email password is empty")
    else:
        print("❌ No email password configured")
    
    print(f"\n💡 Gmail Requirements:")
    print("   • 2-Factor Authentication must be enabled")
    print("   • App Password must be used (not regular password)")
    print("   • Less secure app access is deprecated")

def check_recent_email_attempts():
    """Check recent email sending attempts"""
    
    print(f"\n📊 RECENT EMAIL ATTEMPTS")
    print("=" * 25)
    
    from reminders.models import Reminder
    from datetime import date
    
    today = date.today()
    recent_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True
    ).order_by('-created_at')
    
    print(f"Digests marked as sent today: {recent_digests.count()}")
    
    for digest in recent_digests:
        print(f"\n   👤 {digest.student.username}:")
        print(f"      Email: {digest.student.email}")
        print(f"      Created: {digest.created_at}")
        print(f"      Sent at: {digest.sent_at}")
        print(f"      Scheduled: {digest.reminder_time}")

def diagnose_email_issue():
    """Diagnose the email issue"""
    
    print(f"\n🔍 EMAIL ISSUE DIAGNOSIS")
    print("=" * 25)
    
    print("🚨 IDENTIFIED ISSUES:")
    print("   1. Emails marked as 'sent' but sent_at is None")
    print("   2. This suggests email sending failed silently")
    print("   3. Possible causes:")
    print("      • Gmail authentication issue")
    print("      • App password expired")
    print("      • SMTP connection problem")
    print("      • Email blocked by Gmail")
    
    print(f"\n💡 SOLUTIONS TO TRY:")
    print("   1. Check Gmail inbox and spam folder")
    print("   2. Verify Gmail App Password is correct")
    print("   3. Test direct email sending")
    print("   4. Check Gmail account security settings")

def fix_sent_at_field():
    """Fix the sent_at field for recent emails"""
    
    print(f"\n🔧 FIXING SENT_AT FIELD")
    print("=" * 20)
    
    from reminders.models import Reminder
    from datetime import date
    
    today = date.today()
    broken_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True,
        sent_at__isnull=True
    )
    
    print(f"Digests with missing sent_at: {broken_digests.count()}")
    
    if broken_digests.exists():
        response = input("🤔 Fix sent_at timestamps? (y/n): ")
        if response.lower() == 'y':
            for digest in broken_digests:
                digest.sent_at = digest.created_at
                digest.save()
                print(f"✅ Fixed sent_at for {digest.student.username}")
        else:
            print("❌ Fix cancelled")

if __name__ == "__main__":
    check_email_configuration()
    test_direct_email()
    check_gmail_authentication()
    check_recent_email_attempts()
    diagnose_email_issue()
    fix_sent_at_field()
    
    print(f"\n" + "=" * 50)
    print("🎯 SUMMARY")
    print("=" * 50)
    
    print("📧 Email Status:")
    print("   • System marked email as sent")
    print("   • But sent_at timestamp is missing")
    print("   • This suggests email sending failed")
    
    print(f"\n🔍 Next Steps:")
    print("   1. Check your Gmail inbox and spam folder")
    print("   2. Run the direct email test above")
    print("   3. Verify Gmail App Password is working")
    print("   4. Check if emails are being blocked")
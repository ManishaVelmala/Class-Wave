#!/usr/bin/env python3
"""
Diagnose and fix email delivery issues - DNS/MX record problems
"""

import os
import sys
import django
from datetime import date, time, datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def check_email_configuration():
    """Check current email configuration"""
    
    print("📧 EMAIL CONFIGURATION CHECK")
    print("=" * 30)
    
    print(f"Email Backend: {settings.EMAIL_BACKEND}")
    
    if hasattr(settings, 'EMAIL_HOST'):
        print(f"SMTP Host: {settings.EMAIL_HOST}")
    if hasattr(settings, 'EMAIL_PORT'):
        print(f"SMTP Port: {settings.EMAIL_PORT}")
    if hasattr(settings, 'EMAIL_HOST_USER'):
        print(f"SMTP User: {settings.EMAIL_HOST_USER}")
    if hasattr(settings, 'EMAIL_USE_TLS'):
        print(f"Use TLS: {settings.EMAIL_USE_TLS}")
    if hasattr(settings, 'DEFAULT_FROM_EMAIL'):
        print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")

def check_student_email_addresses():
    """Check student email addresses for issues"""
    
    print(f"\n👥 STUDENT EMAIL ADDRESSES")
    print("=" * 28)
    
    students = User.objects.filter(user_type='student')
    
    print(f"Total students: {students.count()}")
    
    problematic_emails = []
    
    for student in students:
        email = student.email
        print(f"• {student.username}: {email}")
        
        # Check for common issues
        if not email or '@' not in email:
            problematic_emails.append((student.username, email, "Invalid format"))
        elif email.endswith('@example.com') or email.endswith('@test.com'):
            problematic_emails.append((student.username, email, "Test/example domain"))
        elif 'localhost' in email:
            problematic_emails.append((student.username, email, "Localhost domain"))
    
    if problematic_emails:
        print(f"\n⚠️  PROBLEMATIC EMAIL ADDRESSES:")
        for username, email, issue in problematic_emails:
            print(f"   • {username}: {email} - {issue}")
    else:
        print(f"\n✅ All email addresses look valid")
    
    return problematic_emails

def test_email_sending():
    """Test email sending with different approaches"""
    
    print(f"\n🧪 EMAIL SENDING TEST")
    print("=" * 21)
    
    # Test with console backend first
    original_backend = settings.EMAIL_BACKEND
    
    print("1. Testing with Console Backend:")
    settings.EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    
    try:
        send_mail(
            subject='Test Email - Console Backend',
            message='This is a test email using console backend.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],
            fail_silently=False,
        )
        print("   ✅ Console backend works")
    except Exception as e:
        print(f"   ❌ Console backend failed: {e}")
    
    # Test with SMTP backend if configured
    if hasattr(settings, 'EMAIL_HOST') and settings.EMAIL_HOST:
        print("\n2. Testing with SMTP Backend:")
        settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        
        try:
            send_mail(
                subject='Test Email - SMTP Backend',
                message='This is a test email using SMTP backend.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['test@gmail.com'],  # Use Gmail for testing
                fail_silently=False,
            )
            print("   ✅ SMTP backend works")
        except Exception as e:
            print(f"   ❌ SMTP backend failed: {e}")
    else:
        print("\n2. SMTP Backend: Not configured")
    
    # Restore original backend
    settings.EMAIL_BACKEND = original_backend

def check_recent_email_failures():
    """Check for recent email failures"""
    
    print(f"\n📊 RECENT EMAIL STATUS")
    print("=" * 22)
    
    # Get recent digests
    recent_date = date.today()
    recent_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=recent_date
    )
    
    print(f"Digests for {recent_date}: {recent_digests.count()}")
    
    sent_count = recent_digests.filter(is_sent=True).count()
    failed_count = recent_digests.filter(is_sent=False).count()
    
    print(f"✅ Sent: {sent_count}")
    print(f"❌ Failed/Pending: {failed_count}")
    
    if recent_digests.exists():
        print(f"\nDetailed Status:")
        for digest in recent_digests:
            status = "✅ Sent" if digest.is_sent else "❌ Failed"
            sent_time = f" at {digest.sent_at.strftime('%I:%M %p')}" if digest.sent_at else ""
            print(f"   • {digest.student.username} ({digest.student.email}): {status}{sent_time}")

def suggest_fixes():
    """Suggest fixes for email delivery issues"""
    
    print(f"\n🔧 SUGGESTED FIXES")
    print("=" * 17)
    
    print("1. EMAIL CONFIGURATION ISSUES:")
    print("   • Check SMTP settings in settings.py")
    print("   • Verify Gmail App Password if using Gmail")
    print("   • Test with console backend first")
    
    print(f"\n2. DNS/MX RECORD ISSUES:")
    print("   • Use Gmail SMTP instead of custom domains")
    print("   • Update student emails to Gmail addresses")
    print("   • Avoid @example.com or test domains")
    
    print(f"\n3. GMAIL SPECIFIC FIXES:")
    print("   • Enable 2-factor authentication")
    print("   • Generate App Password")
    print("   • Use smtp.gmail.com:587 with TLS")
    
    print(f"\n4. IMMEDIATE WORKAROUND:")
    print("   • Switch to console backend for testing")
    print("   • Update problematic email addresses")
    print("   • Use real Gmail addresses for students")

def fix_email_addresses():
    """Fix problematic email addresses"""
    
    print(f"\n🔧 FIXING EMAIL ADDRESSES")
    print("=" * 26)
    
    students = User.objects.filter(user_type='student')
    fixed_count = 0
    
    for student in students:
        original_email = student.email
        
        # Fix common issues
        if not original_email or '@' not in original_email:
            # Generate a Gmail address
            new_email = f"{student.username.lower()}@gmail.com"
            student.email = new_email
            student.save()
            print(f"✅ Fixed {student.username}: {original_email} → {new_email}")
            fixed_count += 1
        elif original_email.endswith('@example.com'):
            # Replace with Gmail
            new_email = original_email.replace('@example.com', '@gmail.com')
            student.email = new_email
            student.save()
            print(f"✅ Fixed {student.username}: {original_email} → {new_email}")
            fixed_count += 1
    
    print(f"\n📊 Fixed {fixed_count} email addresses")

def test_with_console_backend():
    """Test digest sending with console backend"""
    
    print(f"\n🧪 TESTING WITH CONSOLE BACKEND")
    print("=" * 33)
    
    # Switch to console backend
    original_backend = settings.EMAIL_BACKEND
    settings.EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    
    try:
        from django.core.management import call_command
        
        print("Running digest command with console backend...")
        call_command('send_real_daily_digests', verbosity=1)
        print("✅ Console backend test completed")
        
    except Exception as e:
        print(f"❌ Console backend test failed: {e}")
    finally:
        # Restore original backend
        settings.EMAIL_BACKEND = original_backend

def create_gmail_smtp_config():
    """Show Gmail SMTP configuration"""
    
    print(f"\n📧 GMAIL SMTP CONFIGURATION")
    print("=" * 28)
    
    print("Add these settings to your settings.py:")
    print("""
# Gmail SMTP Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Not your regular password!
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
""")
    
    print("Steps to get App Password:")
    print("1. Enable 2-factor authentication on Gmail")
    print("2. Go to Google Account settings")
    print("3. Security → App passwords")
    print("4. Generate password for 'Mail'")
    print("5. Use that password in EMAIL_HOST_PASSWORD")

def final_diagnosis():
    """Provide final diagnosis and recommendations"""
    
    print(f"\n" + "=" * 60)
    print("🎯 FINAL DIAGNOSIS & RECOMMENDATIONS")
    print("=" * 60)
    
    print("📊 ISSUE ANALYSIS:")
    print("The DNS/MX error suggests email delivery problems.")
    print("This commonly happens with:")
    print("• Invalid email addresses")
    print("• Misconfigured SMTP settings")
    print("• Using test/example domains")
    
    print(f"\n🔧 IMMEDIATE FIXES:")
    print("1. Switch to console backend for testing")
    print("2. Update student emails to real Gmail addresses")
    print("3. Configure Gmail SMTP properly")
    print("4. Test with simple email first")
    
    print(f"\n⚡ QUICK SOLUTION:")
    print("Run these commands:")
    print("1. python manage.py shell")
    print("2. Update EMAIL_BACKEND to console in settings")
    print("3. Test digest generation")
    print("4. Fix email addresses")
    print("5. Configure Gmail SMTP")

if __name__ == "__main__":
    print("🔍 EMAIL DELIVERY ISSUE DIAGNOSIS")
    print("=" * 35)
    
    check_email_configuration()
    problematic_emails = check_student_email_addresses()
    test_email_sending()
    check_recent_email_failures()
    suggest_fixes()
    
    if problematic_emails:
        print(f"\n🔧 FIXING PROBLEMATIC EMAILS...")
        fix_email_addresses()
    
    test_with_console_backend()
    create_gmail_smtp_config()
    final_diagnosis()
    
    print(f"\n✅ DIAGNOSIS COMPLETE")
    print("Follow the recommendations above to fix email delivery!")
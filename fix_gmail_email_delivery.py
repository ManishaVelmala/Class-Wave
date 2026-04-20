#!/usr/bin/env python3
"""
Fix Gmail email delivery issues
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

def test_gmail_connection():
    """Test Gmail SMTP connection"""
    
    print("📧 TESTING GMAIL SMTP CONNECTION")
    print("=" * 34)
    
    print(f"SMTP Host: {settings.EMAIL_HOST}")
    print(f"SMTP Port: {settings.EMAIL_PORT}")
    print(f"SMTP User: {settings.EMAIL_HOST_USER}")
    print(f"Use TLS: {settings.EMAIL_USE_TLS}")
    
    # Test simple email
    try:
        print(f"\n🧪 Sending test email...")
        
        send_mail(
            subject='ClassWave Test Email',
            message='This is a test email from ClassWave system.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],  # Send to self
            fail_silently=False,
        )
        
        print("✅ Test email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test email failed: {e}")
        return False

def send_digest_with_retry():
    """Send digests with retry mechanism"""
    
    print(f"\n📧 SENDING DIGESTS WITH RETRY")
    print("=" * 30)
    
    # Get pending digests
    india_now = timezone.now() + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    current_india_time = india_now.time()
    
    pending_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date,
        is_sent=False
    )
    
    print(f"Pending digests: {pending_digests.count()}")
    print(f"Current India time: {current_india_time.strftime('%I:%M %p')}")
    
    sent_count = 0
    failed_count = 0
    
    for digest in pending_digests:
        student = digest.student
        
        try:
            pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
            student_time = pref.digest_time
            
            # Check if due
            if current_india_time >= student_time:
                print(f"\n📧 Sending to {student.username} ({student.email})")
                
                # Try multiple email formats
                success = send_email_with_formats(student, digest)
                
                if success:
                    sent_count += 1
                    print(f"✅ Sent successfully!")
                else:
                    failed_count += 1
                    print(f"❌ Failed after all attempts")
            else:
                print(f"⏳ {student.username}: Not due yet ({student_time.strftime('%I:%M %p')})")
                
        except DailyDigestPreference.DoesNotExist:
            print(f"⚠️  {student.username}: No preference set")
    
    print(f"\n📊 Results: {sent_count} sent, {failed_count} failed")
    return sent_count, failed_count

def send_email_with_formats(student, digest):
    """Try sending email with different formats"""
    
    formats = [
        {
            'subject': f'📅 Your Schedule for {digest.digest_date.strftime("%A, %B %d")}',
            'message': digest.message
        },
        {
            'subject': f'Your Classes Today - {digest.digest_date.strftime("%B %d")}',
            'message': clean_message(digest.message)
        },
        {
            'subject': 'ClassWave Daily Schedule',
            'message': f"Hello {student.first_name or student.username},\n\nYour classes for today:\n\n{extract_class_info(digest.message)}\n\nBest regards,\nClassWave Team"
        }
    ]
    
    for i, format_info in enumerate(formats, 1):
        try:
            print(f"   Attempt {i}: {format_info['subject'][:30]}...")
            
            send_mail(
                subject=format_info['subject'],
                message=format_info['message'],
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=False,
            )
            
            # Mark as sent
            digest.is_sent = True
            digest.sent_at = timezone.now()
            digest.save()
            
            return True
            
        except Exception as e:
            print(f"   Attempt {i} failed: {str(e)[:50]}...")
            continue
    
    return False

def clean_message(message):
    """Remove emojis and clean message"""
    emojis = ['📅', '📚', '⏰', '👨‍🏫', '📍', '🎓', '💡']
    for emoji in emojis:
        message = message.replace(emoji, '')
    return message.strip()

def extract_class_info(message):
    """Extract basic class information"""
    lines = message.split('\n')
    class_info = []
    
    for line in lines:
        if 'Time:' in line or 'Topic:' in line or 'Lecturer:' in line:
            clean_line = clean_message(line).strip()
            if clean_line:
                class_info.append(clean_line)
    
    return '\n'.join(class_info) if class_info else 'Check your schedule for details.'

def force_send_pending_emails():
    """Force send all pending emails regardless of time"""
    
    print(f"\n🚀 FORCE SENDING ALL PENDING EMAILS")
    print("=" * 36)
    
    india_now = timezone.now() + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    
    pending_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date,
        is_sent=False
    )
    
    print(f"Force sending {pending_digests.count()} pending emails...")
    
    sent_count = 0
    
    for digest in pending_digests:
        student = digest.student
        print(f"\n📧 Force sending to {student.username}")
        
        success = send_email_with_formats(student, digest)
        
        if success:
            sent_count += 1
            print(f"✅ Sent!")
        else:
            print(f"❌ Failed")
    
    print(f"\n📊 Force sent: {sent_count} emails")
    return sent_count

def check_gmail_settings():
    """Check Gmail settings and provide recommendations"""
    
    print(f"\n🔧 GMAIL SETTINGS CHECK")
    print("=" * 24)
    
    issues = []
    
    if not hasattr(settings, 'EMAIL_HOST_PASSWORD'):
        issues.append("EMAIL_HOST_PASSWORD not set")
    
    if settings.EMAIL_HOST != 'smtp.gmail.com':
        issues.append(f"EMAIL_HOST should be 'smtp.gmail.com', got '{settings.EMAIL_HOST}'")
    
    if settings.EMAIL_PORT != 587:
        issues.append(f"EMAIL_PORT should be 587, got {settings.EMAIL_PORT}")
    
    if not settings.EMAIL_USE_TLS:
        issues.append("EMAIL_USE_TLS should be True")
    
    if issues:
        print("⚠️  Configuration Issues:")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print("✅ Gmail configuration looks correct")
    
    print(f"\n💡 Gmail Setup Checklist:")
    print("1. ✅ Enable 2-factor authentication")
    print("2. ✅ Generate App Password (not regular password)")
    print("3. ✅ Use App Password in EMAIL_HOST_PASSWORD")
    print("4. ✅ Allow less secure apps (if needed)")

def create_backup_solution():
    """Create backup solution using console backend"""
    
    print(f"\n💾 BACKUP SOLUTION - CONSOLE BACKEND")
    print("=" * 37)
    
    print("If Gmail continues to fail, use console backend:")
    
    backup_settings = """
# Backup Email Configuration (Console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Or file backend to save emails
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = 'sent_emails'
"""
    
    print(backup_settings)
    
    print("This will:")
    print("• Print emails to console instead of sending")
    print("• Allow system to work without SMTP issues")
    print("• Help debug email content")

if __name__ == "__main__":
    print("🔧 GMAIL EMAIL DELIVERY FIX")
    print("=" * 29)
    
    # Test Gmail connection
    gmail_works = test_gmail_connection()
    
    if gmail_works:
        print("\n✅ Gmail connection working - proceeding with digest sending")
        
        # Send digests with retry
        sent, failed = send_digest_with_retry()
        
        if failed > 0:
            print(f"\n🚀 Some emails failed - trying force send...")
            force_sent = force_send_pending_emails()
    else:
        print("\n❌ Gmail connection failed")
        check_gmail_settings()
        create_backup_solution()
    
    print(f"\n✅ EMAIL DELIVERY FIX COMPLETE")
    print("Check the results above and follow recommendations if needed.")
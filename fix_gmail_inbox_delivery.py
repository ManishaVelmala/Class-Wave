#!/usr/bin/env python3
"""
Fix Gmail inbox delivery - ensure emails actually reach Gmail inbox
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
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def test_gmail_inbox_delivery():
    """Test different email formats to ensure Gmail inbox delivery"""
    
    print("📧 TESTING GMAIL INBOX DELIVERY")
    print("=" * 35)
    
    test_email = "velmalamallikarjun2@gmail.com"
    
    # Test different approaches to bypass Gmail filtering
    email_tests = [
        {
            'name': 'Plain Text - No Emojis',
            'subject': 'ClassWave Daily Schedule',
            'message': '''Hello Manisha,

Your classes for Tuesday, December 16, 2025:

Morning Classes:
- Deep Learning at 9:30 AM
- Information Security at 10:25 AM

Afternoon Classes:
- Internet Technologies at 1:00 PM

Have a great day!

Best regards,
ClassWave Team'''
        },
        {
            'name': 'Personal Format',
            'subject': 'Your Classes Today',
            'message': '''Hi Manisha,

Hope you're doing well! Here are your classes for today:

9:30 AM - Deep Learning
10:25 AM - Information Security
1:00 PM - Internet Technologies

Don't forget to check your schedule!

Regards,
ClassWave'''
        },
        {
            'name': 'Simple Reminder',
            'subject': 'Class Reminder',
            'message': '''Dear Student,

You have 3 classes scheduled for today.

Please check your ClassWave dashboard for details.

Thank you,
ClassWave System'''
        },
        {
            'name': 'HTML Email',
            'subject': 'Daily Class Schedule',
            'html_message': '''<html><body>
<h2>Your Classes Today</h2>
<p>Hello Manisha,</p>
<ul>
<li><strong>9:30 AM</strong> - Deep Learning</li>
<li><strong>10:25 AM</strong> - Information Security</li>
<li><strong>1:00 PM</strong> - Internet Technologies</li>
</ul>
<p>Have a great day!</p>
<p>Best regards,<br>ClassWave Team</p>
</body></html>''',
            'text_message': '''Your Classes Today

Hello Manisha,

9:30 AM - Deep Learning
10:25 AM - Information Security
1:00 PM - Internet Technologies

Have a great day!

Best regards,
ClassWave Team'''
        }
    ]
    
    successful_formats = []
    
    for i, email_test in enumerate(email_tests, 1):
        try:
            print(f"📧 Test {i}: {email_test['name']}")
            
            if 'html_message' in email_test:
                # Send HTML email
                msg = EmailMessage(
                    subject=email_test['subject'],
                    body=email_test['html_message'],
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[test_email],
                )
                msg.content_subtype = "html"
                msg.send()
            else:
                # Send plain text email
                send_mail(
                    subject=email_test['subject'],
                    message=email_test['message'],
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[test_email],
                    fail_silently=False,
                )
            
            print(f"   ✅ Sent successfully")
            successful_formats.append(email_test['name'])
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print(f"\n📊 Test Results:")
    print(f"   Successful formats: {len(successful_formats)}")
    for format_name in successful_formats:
        print(f"   ✅ {format_name}")
    
    return successful_formats

def create_gmail_friendly_email_service():
    """Create an email service optimized for Gmail delivery"""
    
    print(f"\n🔧 CREATING GMAIL-FRIENDLY EMAIL SERVICE")
    print("=" * 40)
    
    gmail_service = '''from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from accounts.models import User
from reminders.tasks import create_daily_digest_for_student
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from reminders.models import Reminder, DailyDigestPreference

class Command(BaseCommand):
    help = 'Gmail-optimized daily digest email delivery'

    def add_arguments(self, parser):
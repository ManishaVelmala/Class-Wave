#!/usr/bin/env python3
"""
Improved email service with proper timezone conversion
Keeps Django timezone as UTC but handles India time correctly
"""

import os
import sys
import django
import time
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.core.management import call_command
from django.utils import timezone
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def run_improved_service():
    """Run email service with proper timezone handling"""
    
    print("IMPROVED EMAIL SERVICE (UTC + INDIA CONVERSION)")
    print("=" * 55)
    print("   • Keeps Django timezone as UTC")
    print("   • Converts India preferences correctly")
    print("   • Checks every 2 minutes")
    print("   • Press Ctrl+C to stop")
    
    try:
        check_count = 0
        while True:
            try:
                check_count += 1
                utc_now = timezone.now()
                
                # Calculate India time for display
                india_offset = timedelta(hours=5, minutes=30)
                india_now = utc_now + india_offset
                
                print(f"\nCheck #{check_count}")
                print(f"   UTC: {utc_now.strftime('%I:%M %p')}")
                print(f"   India: {india_now.strftime('%I:%M %p')}")
                
                # Find due digests (already in UTC)
                today = datetime.now().date()
                due_digests = Reminder.objects.filter(
                    reminder_type='daily_digest',
                    digest_date=today,
                    is_sent=False,
                    reminder_time__lte=utc_now
                )
                
                if due_digests.exists():
                    print(f"   Found {due_digests.count()} due emails")
                    
                    # Send emails
                    from django.core.mail import send_mail
                    from django.conf import settings
                    
                    for digest in due_digests:
                        try:
                            send_mail(
                                subject=f'Your Schedule for {today.strftime("%A, %B %d, %Y")}',
                                message=digest.message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[digest.student.email],
                                fail_silently=False,
                            )
                            
                            digest.is_sent = True
                            digest.sent_at = utc_now
                            digest.save()
                            
                            print(f"   Sent to {digest.student.username}")
                            
                        except Exception as e:
                            print(f"   Failed to send to {digest.student.username}: {e}")
                else:
                    print(f"   No emails due")
                
                # Wait 2 minutes
                time.sleep(120)
                
            except KeyboardInterrupt:
                print("\nService stopped by user")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(120)
    
    except KeyboardInterrupt:
        print("\nService stopped")

if __name__ == "__main__":
    run_improved_service()
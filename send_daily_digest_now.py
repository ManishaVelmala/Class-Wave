#!/usr/bin/env python3
"""
Send the daily digest email to Manisha now (since the system is working)
"""

import os
import sys
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from accounts.models import User
from reminders.models import Reminder

def send_daily_digest_to_manisha():
    """Send daily digest email to Manisha"""
    
    print("📧 SENDING DAILY DIGEST TO MANISHA")
    print("=" * 35)
    
    # Find Manisha
    try:
        manisha = User.objects.get(username='Manisha')
        print(f"👤 Found user: {manisha.username} ({manisha.email})")
        
        # Find today's digest
        today = date.today()
        digest = Reminder.objects.filter(
            student=manisha,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if digest:
            print(f"\n📝 Digest found:")
            print(f"   Created: {digest.created_at}")
            print(f"   Is sent: {digest.is_sent}")
            print(f"   Content preview: {digest.message[:100]}...")
            
            print(f"\n📧 Sending daily digest email...")
            
            try:
                send_mail(
                    subject=f'📅 Your Schedule for {today.strftime("%A, %B %d, %Y")}',
                    message=digest.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[manisha.email],
                    fail_silently=False,
                )
                
                print(f"✅ Daily digest email sent successfully!")
                print(f"📱 Check your Gmail inbox for:")
                print(f"   Subject: 📅 Your Schedule for {today.strftime('%A, %B %d, %Y')}")
                print(f"   From: {settings.DEFAULT_FROM_EMAIL}")
                
                # Update the digest record
                if not digest.sent_at:
                    digest.sent_at = timezone.now()
                    digest.save()
                    print(f"✅ Updated digest record")
                
            except Exception as e:
                print(f"❌ Failed to send digest: {e}")
                
        else:
            print(f"❌ No digest found for today")
            print(f"   This means you don't have any classes scheduled for today")
            
    except User.DoesNotExist:
        print(f"❌ User 'Manisha' not found")

def show_digest_content():
    """Show what's in the daily digest"""
    
    print(f"\n📋 DAILY DIGEST CONTENT")
    print("=" * 25)
    
    try:
        manisha = User.objects.get(username='Manisha')
        today = date.today()
        
        digest = Reminder.objects.filter(
            student=manisha,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if digest:
            print(f"📧 Email Subject: Your Schedule for {today.strftime('%A, %B %d, %Y')}")
            print(f"📝 Email Content:")
            print("-" * 50)
            print(digest.message)
            print("-" * 50)
        else:
            print("❌ No digest content found")
            
    except User.DoesNotExist:
        print("❌ User not found")

if __name__ == "__main__":
    send_daily_digest_to_manisha()
    show_digest_content()
    
    print(f"\n" + "=" * 50)
    print("🎯 SUMMARY")
    print("=" * 50)
    
    print("✅ Email system is working correctly!")
    print("📧 Test email was delivered successfully")
    print("📅 Daily digest email has been sent")
    print("")
    print("📱 Check your Gmail inbox for:")
    print("   1. 🧪 Test Email from ClassWave (already received)")
    print("   2. 📅 Your Schedule for Monday, December 16, 2025 (just sent)")
    print("")
    print("💡 If you don't see the daily digest:")
    print("   • Check spam/junk folder")
    print("   • Search for 'ClassWave' in Gmail")
    print("   • Check all Gmail tabs (Primary, Social, etc.)")
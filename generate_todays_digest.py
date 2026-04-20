#!/usr/bin/env python
"""
Generate today's daily digest for all students
"""

import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from reminders.tasks import create_daily_digest_for_student
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

def generate_todays_digest():
    today = date.today()
    print(f"🗓️  GENERATING DIGEST FOR: {today}")
    print("=" * 50)
    
    students = User.objects.filter(user_type='student')
    
    generated_count = 0
    sent_count = 0
    
    for student in students:
        print(f"\n👤 Processing: {student.username} ({student.email})")
        
        # Generate digest for today
        digest = create_daily_digest_for_student(student.id, today)
        
        if digest:
            generated_count += 1
            print(f"   ✅ Digest created for {today}")
            
            # Send email
            try:
                send_mail(
                    subject=f'📅 Your Schedule for {today.strftime("%A, %B %d, %Y")}',
                    message=digest.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[student.email],
                    fail_silently=False,
                )
                
                # Mark as sent (this makes it appear in notification bar)
                digest.is_sent = True
                digest.sent_at = timezone.now()
                digest.save()
                
                sent_count += 1
                print(f"   📧 Email sent and marked as sent")
                print(f"   📱 Will appear in notification bar")
                
            except Exception as e:
                print(f"   ❌ Email failed: {e}")
        else:
            print(f"   ℹ️  No classes for {student.username} on {today}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Date: {today}")
    print(f"   Students processed: {students.count()}")
    print(f"   Digests generated: {generated_count}")
    print(f"   Emails sent: {sent_count}")
    
    if sent_count > 0:
        print(f"\n✅ SUCCESS!")
        print(f"   📧 Digests sent to Gmail inboxes")
        print(f"   📱 Digests will appear in notification bar")
        print(f"   🗓️  Students will see {today} schedule instead of old dates")

if __name__ == "__main__":
    generate_todays_digest()
#!/usr/bin/env python3
"""
Fix all digest times to match student preferences
"""

import os
import sys
import django
from datetime import date, time, datetime
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def fix_all_digest_times():
    """Fix all digest times to match student preferences"""
    
    print("🔧 FIXING ALL DIGEST TIMES")
    print("=" * 40)
    
    today = date.today()
    fixed_count = 0
    
    # Get all students with preferences
    all_prefs = DailyDigestPreference.objects.filter(is_enabled=True)
    
    print(f"👥 Students with preferences: {all_prefs.count()}")
    
    for pref in all_prefs:
        student = pref.student
        preference_time = pref.digest_time
        
        print(f"\n👤 Checking {student.username}:")
        print(f"   Preference: {preference_time.strftime('%I:%M %p')}")
        
        # Find today's digest
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if digest:
            # Calculate correct reminder time
            correct_datetime = datetime.combine(today, preference_time)
            correct_datetime = timezone.make_aware(correct_datetime)
            
            old_time = digest.reminder_time
            
            print(f"   📅 Current digest time: {old_time}")
            print(f"   📅 Should be: {correct_datetime}")
            
            # Check if times match
            if digest.reminder_time.time() != preference_time:
                print(f"   ⚠️  TIME MISMATCH - Fixing...")
                
                # Update the digest
                digest.reminder_time = correct_datetime
                digest.is_sent = False  # Reset sent status
                digest.save()
                
                print(f"   ✅ Fixed digest time")
                fixed_count += 1
            else:
                print(f"   ✅ Time already correct")
        else:
            print(f"   📝 No digest found - will be created on next website visit")
    
    print(f"\n📊 Fixed {fixed_count} digest times")
    
    return fixed_count

def recreate_problematic_digests():
    """Recreate digests that have wrong times"""
    
    print(f"\n🔄 RECREATING PROBLEMATIC DIGESTS")
    print("=" * 45)
    
    today = date.today()
    recreated_count = 0
    
    # Find digests with mismatched times
    all_prefs = DailyDigestPreference.objects.filter(is_enabled=True)
    
    for pref in all_prefs:
        student = pref.student
        preference_time = pref.digest_time
        
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if digest and digest.reminder_time.time() != preference_time:
            print(f"👤 Recreating digest for {student.username}...")
            
            # Delete old digest
            old_id = digest.id
            digest.delete()
            print(f"   🗑️  Deleted old digest (ID: {old_id})")
            
            # Create new digest with correct time
            from reminders.tasks import create_daily_digest_for_student
            
            try:
                new_digest = create_daily_digest_for_student(student.id, today)
                if new_digest:
                    print(f"   ✅ Created new digest (ID: {new_digest.id})")
                    print(f"      Scheduled for: {new_digest.reminder_time}")
                    recreated_count += 1
                else:
                    print(f"   ❌ No new digest created (no classes today)")
            except Exception as e:
                print(f"   ❌ Error creating new digest: {e}")
    
    print(f"\n📊 Recreated {recreated_count} digests")
    return recreated_count

def verify_all_digest_times():
    """Verify all digest times are correct"""
    
    print(f"\n✅ VERIFICATION: ALL DIGEST TIMES")
    print("=" * 40)
    
    today = date.today()
    all_correct = True
    
    all_prefs = DailyDigestPreference.objects.filter(is_enabled=True)
    
    for pref in all_prefs:
        student = pref.student
        preference_time = pref.digest_time
        
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if digest:
            digest_time = digest.reminder_time.time()
            matches = digest_time == preference_time
            
            status = "✅" if matches else "❌"
            print(f"   {status} {student.username}:")
            print(f"      Preference: {preference_time.strftime('%I:%M %p')}")
            print(f"      Digest time: {digest_time.strftime('%I:%M %p')}")
            
            if not matches:
                all_correct = False
        else:
            print(f"   ⚠️  {student.username}: No digest found")
    
    if all_correct:
        print(f"\n🎉 ALL DIGEST TIMES ARE CORRECT!")
    else:
        print(f"\n❌ SOME DIGEST TIMES ARE STILL WRONG!")
    
    return all_correct

def send_due_emails_now():
    """Send any emails that are due now"""
    
    print(f"\n📧 SENDING DUE EMAILS")
    print("=" * 30)
    
    today = date.today()
    now = timezone.now()
    
    due_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=False,
        reminder_time__lte=now
    )
    
    print(f"📧 Due digests: {due_digests.count()}")
    
    if not due_digests.exists():
        print("📭 No emails due to be sent")
        return 0
    
    from django.core.mail import send_mail
    from django.conf import settings
    
    sent_count = 0
    
    for digest in due_digests:
        try:
            print(f"   📤 Sending to {digest.student.username}...")
            
            send_mail(
                subject=f'📅 Your Schedule for {digest.digest_date.strftime("%A, %B %d, %Y")}',
                message=digest.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[digest.student.email],
                fail_silently=False,
            )
            
            # Mark as sent
            digest.is_sent = True
            digest.sent_at = now
            digest.save()
            
            print(f"   ✅ Email sent to {digest.student.email}")
            sent_count += 1
            
        except Exception as e:
            print(f"   ❌ Failed to send to {digest.student.email}: {e}")
    
    print(f"\n📊 Successfully sent {sent_count} emails")
    return sent_count

if __name__ == "__main__":
    # Step 1: Try to fix existing digest times
    fixed_count = fix_all_digest_times()
    
    # Step 2: If fixing didn't work, recreate problematic digests
    if fixed_count == 0:
        print("\n🔄 No digests were fixed, trying recreation...")
        recreate_problematic_digests()
    
    # Step 3: Verify all times are correct
    all_correct = verify_all_digest_times()
    
    # Step 4: Send due emails
    if all_correct:
        response = input("\n🤔 Do you want to send due emails now? (y/n): ")
        if response.lower() == 'y':
            send_due_emails_now()
    
    print("\n" + "=" * 40)
    print("🎯 SUMMARY:")
    if all_correct:
        print("   ✅ All digest times are now correct")
        print("   📧 Emails will be sent at student preferences")
    else:
        print("   ❌ Some digest times are still incorrect")
        print("   🔧 Manual intervention may be needed")
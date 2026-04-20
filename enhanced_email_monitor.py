#!/usr/bin/env python3
import os, sys, django
from datetime import datetime, timedelta, time, date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def monitor_all_students():
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    current_india_time = india_now.time()
    india_date = india_now.date()
    
    print("EMAIL DELIVERY MONITORING")
    print("=" * 29)
    print(f"Current India time: {current_india_time.strftime('%I:%M %p')}")
    print(f"Monitoring date: {india_date}")
    
    students = User.objects.filter(user_type='student')
    overdue_count = 0
    
    for student in students:
        try:
            pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
            student_time = pref.digest_time
            
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=india_date
            ).first()
            
            is_due = current_india_time >= student_time
            
            if digest and digest.is_sent:
                india_sent_time = digest.sent_at + timedelta(hours=5, minutes=30)
                print(f"✅ {student.username}: Sent at {india_sent_time.strftime('%I:%M %p India')}")
            elif is_due and digest and not digest.is_sent:
                time_overdue = datetime.combine(date.today(), current_india_time) - datetime.combine(date.today(), student_time)
                minutes_overdue = int(time_overdue.total_seconds() // 60)
                print(f"🚨 {student.username}: OVERDUE by {minutes_overdue} minutes (due at {student_time.strftime('%I:%M %p')})")
                overdue_count += 1
                
                # Auto-fix if overdue
                try:
                    send_mail(
                        subject=f'Your Schedule for {india_date.strftime("%A, %B %d")}',
                        message=digest.message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[student.email],
                        fail_silently=False,
                    )
                    
                    digest.is_sent = True
                    digest.sent_at = timezone.now()
                    digest.save()
                    
                    print(f"   ✅ AUTO-FIXED: Email sent successfully!")
                    
                except Exception as e:
                    print(f"   ❌ AUTO-FIX FAILED: {e}")
                    
            elif not is_due and digest:
                time_until = datetime.combine(date.today(), student_time) - datetime.combine(date.today(), current_india_time)
                minutes_until = int(time_until.total_seconds() // 60)
                print(f"⏳ {student.username}: Due in {minutes_until} minutes (at {student_time.strftime('%I:%M %p')})")
            else:
                print(f"⚠️  {student.username}: No digest found!")
                
        except DailyDigestPreference.DoesNotExist:
            print(f"⚠️  {student.username}: No preference set")
    
    print(f"\nMONITORING COMPLETE - Fixed {overdue_count} overdue emails")
    return overdue_count

if __name__ == "__main__":
    monitor_all_students()

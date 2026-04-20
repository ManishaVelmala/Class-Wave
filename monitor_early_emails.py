#!/usr/bin/env python3
"""
Monitor for early email delivery
Run this daily to check if any emails were sent too early
"""

import os, sys, django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.utils import timezone
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def check_for_early_emails():
    """Check if any emails were sent too early today"""
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    
    print(f"🔍 Checking for early emails on {india_date}")
    
    early_count = 0
    
    for student in User.objects.filter(user_type='student'):
        try:
            pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=india_date,
                is_sent=True
            ).first()
            
            if digest and digest.sent_at:
                sent_time = (digest.sent_at + timedelta(hours=5, minutes=30)).time()
                pref_time = pref.digest_time
                
                if sent_time < pref_time:
                    time_diff = datetime.combine(india_date, pref_time) - datetime.combine(india_date, sent_time)
                    hours_early = time_diff.total_seconds() / 3600
                    
                    if hours_early > 0.5:  # More than 30 minutes early
                        print(f"🚨 EARLY EMAIL: {student.username}")
                        print(f"   Preference: {pref_time.strftime('%I:%M %p')}")
                        print(f"   Sent: {sent_time.strftime('%I:%M %p')}")
                        print(f"   Early by: {hours_early:.1f} hours")
                        early_count += 1
        except:
            continue
    
    if early_count == 0:
        print("✅ No early emails detected")
    else:
        print(f"🚨 {early_count} early emails detected!")
    
    return early_count

if __name__ == "__main__":
    check_for_early_emails()
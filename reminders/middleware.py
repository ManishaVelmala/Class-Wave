"""
Middleware to automatically generate daily digests
"""

from datetime import date
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User
from reminders.models import Reminder
from reminders.tasks import create_daily_digest_for_student


class AutoDigestMiddleware:
    """
    Middleware that automatically generates daily digests for all students
    when any user accesses the system for the first time each day
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self._last_digest_date = None
        self._last_send_check = None
    
    def __call__(self, request):
        from datetime import datetime, timedelta
        
        today = date.today()
        now = datetime.now()
        
        # DAILY CLEANUP: Remove old digests, keep only today's
        if self._last_digest_date != today:
            self._cleanup_old_digests(today)
        
        # Generate digests once per day (for ANY request, not just authenticated)
        if self._last_digest_date != today:
            self._generate_daily_digests_for_all_students(today)
            self._last_digest_date = today
        
        # REMOVED: Don't send emails from middleware
        # Emails should only be sent by the background service at preferred times
        # This prevents immediate email sending when students visit the website
        
        response = self.get_response(request)
        return response
    
    def _generate_daily_digests_for_all_students(self, target_date):
        """Generate daily digests for all students if they don't exist"""
        try:
            students = User.objects.filter(user_type='student')
            
            for student in students:
                # Check if digest already exists for this student and date
                existing_digest = Reminder.objects.filter(
                    student=student,
                    reminder_type='daily_digest',
                    digest_date=target_date
                ).first()
                
                if not existing_digest:
                    # Generate digest
                    digest = create_daily_digest_for_student(student.id, target_date)
                    
                    if digest:
                        # Don't send email immediately - let background service handle timing
                        # Email will be sent at student's preferred time
                        pass
        
        except Exception:
            pass  # Don't break the request if digest generation fails
    
    def _send_due_digests(self):
        """DISABLED: Don't send emails from middleware
        
        This method has been disabled to prevent immediate email sending
        when students visit the website. Emails should only be sent by
        the background service (Windows Task Scheduler) at students' 
        preferred times.
        """
        # REMOVED: All email sending logic
        # Emails are now handled exclusively by:
        # - reminders/management/commands/send_real_daily_digests.py
        # - Windows Task Scheduler running at 6:00 AM daily
        pass
    
    def _cleanup_old_digests(self, today):
        """Remove all past and future digests, keep only today's"""
        try:
            # Delete all digests except today's
            old_digests = Reminder.objects.filter(
                reminder_type='daily_digest'
            ).exclude(digest_date=today)
            
            deleted_count = old_digests.count()
            if deleted_count > 0:
                old_digests.delete()
                print(f"🧹 Cleaned up {deleted_count} old digests, keeping only {today}")
        
        except Exception:
            pass  # Don't break the request
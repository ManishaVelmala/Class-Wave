import win32serviceutil
import win32service
import win32event
import servicemanager
import time
import os
import sys
import django
from datetime import date, datetime, timedelta

# Setup Django
sys.path.append(r'C:\Users\velma\OneDrive\Desktop\Lecturebuzz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference
from reminders.tasks import create_daily_digest_for_student

class ClassWave30SecondService(win32serviceutil.ServiceFramework):
    _svc_name_ = "ClassWave30SecondEmail"
    _svc_display_name_ = "ClassWave 30-Second Email Service"
    _svc_description_ = "Delivers emails with 30-second accuracy for perfect time preferences"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        self.last_digest_date = None
        self.last_check_minute = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, 'ClassWave 30-Second Email Service Started'))
        self.main()

    def main(self):
        while self.running:
            try:
                # Generate digests once per day
                self.check_digest_generation()
                
                # Check for due emails every 30 seconds
                self.check_due_emails()
                
                # Wait 30 seconds before next check
                if win32event.WaitForSingleObject(self.hWaitStop, 30000) == win32event.WAIT_OBJECT_0:
                    break
                    
            except Exception as e:
                servicemanager.LogErrorMsg(f"Email service error: {e}")
                time.sleep(60)

    def check_digest_generation(self):
        today = date.today()
        if self.last_digest_date != today:
            students = User.objects.filter(user_type='student')
            for student in students:
                existing_digest = Reminder.objects.filter(
                    student=student,
                    reminder_type='daily_digest',
                    digest_date=today
                ).first()
                
                if not existing_digest:
                    create_daily_digest_for_student(student.id, today)
            
            self.last_digest_date = today

    def check_due_emails(self):
        utc_now = timezone.now()
        today = date.today()
        current_minute = utc_now.replace(second=0, microsecond=0)
        
        # Only check once per minute to avoid duplicates
        if self.last_check_minute == current_minute:
            return
        
        self.last_check_minute = current_minute
        
        unsent_digests = Reminder.objects.filter(
            reminder_type='daily_digest',
            digest_date=today,
            is_sent=False
        )
        
        for digest in unsent_digests:
            student = digest.student
            try:
                pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
                india_time = pref.digest_time
                
                india_offset = timedelta(hours=5, minutes=30)
                utc_equivalent_time = (
                    datetime.combine(today, india_time) - india_offset
                ).time()
                
                utc_equivalent_datetime = timezone.make_aware(
                    datetime.combine(today, utc_equivalent_time)
                )
                
                if utc_now >= utc_equivalent_datetime:
                    self.send_email(student, digest, today)
                    
            except DailyDigestPreference.DoesNotExist:
                continue

    def send_email(self, student, digest, target_date):
        try:
            send_mail(
                subject=f'Your Schedule for {target_date.strftime("%A, %B %d")}',
                message=digest.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=False,
            )
            
            digest.is_sent = True
            digest.sent_at = timezone.now()
            digest.save()
            
            servicemanager.LogInfoMsg(f"Email sent to {student.username}")
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"Failed to send email to {student.username}: {e}")

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(ClassWave30SecondService)

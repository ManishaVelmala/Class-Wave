from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta, datetime, time
from accounts.models import User
from reminders.tasks import create_daily_digest_for_student
from django.core.mail import send_mail
from django.conf import settings
from reminders.models import Reminder, DailyDigestPreference
import threading
import time as time_module

class Command(BaseCommand):
    help = 'Automatically generate and send daily digests based on student preferences - runs continuously'

    def add_arguments(self, parser):
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Run as daemon (continuous background process)',
        )

    def handle(self, *args, **options):
        if options['daemon']:
            self.stdout.write('🤖 Starting automatic daily digest daemon...')
            self.run_daemon()
        else:
            self.stdout.write('📅 Running one-time digest generation...')
            self.generate_digests_for_today()

    def run_daemon(self):
        """Run continuously and generate digests at appropriate times"""
        self.stdout.write('🔄 Daemon mode: Checking every 5 minutes for digest generation...')
        
        last_check_date = None
        
        while True:
            try:
                current_date = date.today()
                current_time = datetime.now().time()
                
                # Check if we need to generate digests for today
                if last_check_date != current_date:
                    self.stdout.write(f'📅 New day detected: {current_date}')
                    self.generate_digests_for_today()
                    last_check_date = current_date
                
                # Also check if any digests are due to be sent
                self.send_due_digests()
                
                # Wait 5 minutes before next check
                time_module.sleep(300)  # 5 minutes
                
            except KeyboardInterrupt:
                self.stdout.write('🛑 Daemon stopped by user')
                break
            except Exception as e:
                self.stdout.write(f'⚠️ Error in daemon: {e}')
                time_module.sleep(60)  # Wait 1 minute on error

    def generate_digests_for_today(self):
        """Generate digests for all students for today"""
        today = date.today()
        
        students = User.objects.filter(user_type='student')
        generated_count = 0
        
        for student in students:
            # Check if digest already exists for today
            existing_digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=today
            ).first()
            
            if existing_digest:
                continue  # Skip if already generated
            
            # Generate digest
            digest = create_daily_digest_for_student(student.id, today)
            if digest:
                generated_count += 1
                self.stdout.write(f'✅ Generated digest for {student.username}')
        
        if generated_count > 0:
            self.stdout.write(f'📊 Generated {generated_count} new digests for {today}')
        
        return generated_count

    def send_due_digests(self):
        """Send digests that are due based on student preferences"""
        now = timezone.now()
        current_time = now.time()
        
        # Find digests that should be sent now (within 5-minute window)
        due_digests = Reminder.objects.filter(
            reminder_type='daily_digest',
            is_sent=False,
            reminder_time__lte=now,
            reminder_time__gte=now - timedelta(minutes=5)
        )
        
        sent_count = 0
        for digest in due_digests:
            try:
                # Send email
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
                
                sent_count += 1
                self.stdout.write(f'📧 Sent digest to {digest.student.email}')
                
            except Exception as e:
                self.stdout.write(f'❌ Failed to send to {digest.student.email}: {e}')
        
        if sent_count > 0:
            self.stdout.write(f'📊 Sent {sent_count} digests')
        
        return sent_count
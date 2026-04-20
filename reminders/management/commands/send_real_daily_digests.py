from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta, datetime
from accounts.models import User
from reminders.tasks import create_daily_digest_for_student
from django.core.mail import send_mail
from django.conf import settings
from reminders.models import Reminder, DailyDigestPreference

class Command(BaseCommand):
    help = 'Generate and send REAL daily digest emails to student Gmail inboxes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date to generate digests for (YYYY-MM-DD). Default is today.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regenerate digests even if they already exist',
        )

    def handle(self, *args, **options):
        # Parse target date
        if options['date']:
            try:
                target_date = date.fromisoformat(options['date'])
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Invalid date format. Use YYYY-MM-DD')
                )
                return
        else:
            # Use India date instead of UTC date
            utc_now = timezone.now()
            india_now = utc_now + timedelta(hours=5, minutes=30)
            target_date = india_now.date()
        
        force = options['force']
        
        self.stdout.write(f'📅 Generating daily digests for {target_date}...')
        
        # Temporarily switch to SMTP backend for real email sending
        original_backend = settings.EMAIL_BACKEND
        
        # Use console backend if no SMTP is configured, otherwise use SMTP
        if hasattr(settings, 'EMAIL_HOST') and settings.EMAIL_HOST:
            settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
            self.stdout.write('📧 Using SMTP backend for real email delivery')
        else:
            settings.EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
            self.stdout.write('📧 Using console backend (configure SMTP for real emails)')
        
        # Get all students
        students = User.objects.filter(user_type='student')
        
        generated_count = 0
        sent_count = 0
        skipped_count = 0
        
        # PHASE 1: Generate digests for students who don't have them
        for student in students:
            # Check if digest already exists
            existing_digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=target_date
            ).first()
            
            if existing_digest and not force:
                skipped_count += 1
                self.stdout.write(f'⏭️  Skipped {student.username} (digest already exists)')
                continue
            
            # Generate digest for target date
            if existing_digest and force:
                # Delete existing and recreate
                existing_digest.delete()
            
            digest = create_daily_digest_for_student(student.id, target_date)
            
            if digest:
                generated_count += 1
                self.stdout.write(f'📝 Generated digest for {student.username}')
            else:
                self.stdout.write(f'ℹ️  No classes for {student.username} on {target_date}')
        
        # PHASE 2: Send emails for digests that are due (using India time comparison)
        utc_now = timezone.now()
        india_now = utc_now + timedelta(hours=5, minutes=30)
        current_india_time = india_now.time()
        
        # Find all unsent digests for target date (India date)
        unsent_digests = Reminder.objects.filter(
            reminder_type='daily_digest',
            digest_date=target_date,
            is_sent=False
        )
        
        self.stdout.write(f'\n📧 Checking {unsent_digests.count()} unsent digests for due emails...')
        self.stdout.write(f'Current India time: {current_india_time.strftime("%I:%M %p")}')
        
        for digest in unsent_digests:
            student = digest.student
            
            # Get student's time preference (India time)
            try:
                pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
                student_india_time = pref.digest_time
                
                # Compare India times directly with safety check
                if current_india_time >= student_india_time:
                    # Safety check: Don't send emails more than 2 hours early
                    time_diff = datetime.combine(target_date, current_india_time) - datetime.combine(target_date, student_india_time)
                    
                    if time_diff.total_seconds() < -7200:  # More than 2 hours early
                        self.stdout.write(f'⚠️  {student.username}: Skipping - would be {abs(time_diff.total_seconds()//3600):.0f}h early')
                        continue
                    # Time to send email!
                    try:
                        send_mail(
                            subject=f'📅 Your Schedule for {target_date.strftime("%A, %B %d, %Y")}',
                            message=digest.message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[student.email],
                            fail_silently=False,
                        )
                        
                        # Mark as sent
                        digest.is_sent = True
                        digest.sent_at = utc_now
                        digest.save()
                        
                        sent_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Sent to {student.username} ({student.email}) - India time: {student_india_time.strftime("%I:%M %p")}')
                        )
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'❌ Failed to send to {student.username}: {e}')
                        )
                else:
                    # Not time yet - calculate time remaining in India time
                    student_datetime = datetime.combine(target_date, student_india_time)
                    current_datetime = datetime.combine(target_date, current_india_time)
                    
                    if student_datetime > current_datetime:
                        time_until = student_datetime - current_datetime
                        hours = int(time_until.total_seconds() // 3600)
                        minutes = int((time_until.total_seconds() % 3600) // 60)
                        self.stdout.write(f'⏳ {student.username}: Email due in {hours}h {minutes}m (India: {student_india_time.strftime("%I:%M %p")})')
                    else:
                        # Time has passed for today, will send tomorrow
                        self.stdout.write(f'⏳ {student.username}: Email due tomorrow at {student_india_time.strftime("%I:%M %p")} India')
                    
            except DailyDigestPreference.DoesNotExist:
                # No preference set, skip
                self.stdout.write(f'⚠️  {student.username}: No time preference set')
                continue
        
        # Restore original backend
        settings.EMAIL_BACKEND = original_backend
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'📊 Summary:'))
        self.stdout.write(f'   Date: {target_date}')
        self.stdout.write(f'   Students processed: {students.count()}')
        self.stdout.write(f'   Digests generated: {generated_count}')
        self.stdout.write(f'   Emails sent: {sent_count}')
        self.stdout.write(f'   Skipped (existing): {skipped_count}')
        
        if sent_count > 0:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('🎉 SUCCESS!'))
            self.stdout.write('📧 Students should receive emails in their Gmail inboxes')
            self.stdout.write('📱 Digests will also appear in ClassWave notification bar')
        
        if generated_count == 0 and skipped_count == 0:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('⚠️  No digests generated - no classes scheduled for this date'))
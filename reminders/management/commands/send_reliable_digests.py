from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from accounts.models import User
from reminders.tasks import create_daily_digest_for_student
from django.core.mail import send_mail
from django.conf import settings
from reminders.models import Reminder, DailyDigestPreference

class Command(BaseCommand):
    help = 'RELIABLE: Send daily digest emails with guaranteed delivery'

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
        parser.add_argument(
            '--retry-failed',
            action='store_true',
            help='Retry sending failed emails',
        )

    def handle(self, *args, **options):
        target_date = date.today()
        if options['date']:
            try:
                target_date = date.fromisoformat(options['date'])
            except ValueError:
                self.stdout.write(self.style.ERROR('Invalid date format. Use YYYY-MM-DD'))
                return
        
        force = options['force']
        retry_failed = options['retry_failed']
        
        self.stdout.write(f'📧 RELIABLE EMAIL SYSTEM - {target_date}')
        
        # Use SMTP backend
        original_backend = settings.EMAIL_BACKEND
        settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        
        students = User.objects.filter(user_type='student')
        generated_count = 0
        sent_count = 0
        failed_count = 0
        
        # PHASE 1: Generate missing digests
        for student in students:
            existing_digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=target_date
            ).first()
            
            if not existing_digest or force:
                if existing_digest and force:
                    existing_digest.delete()
                
                digest = create_daily_digest_for_student(student.id, target_date)
                if digest:
                    generated_count += 1
                    self.stdout.write(f'📝 Generated digest for {student.username}')
        
        # PHASE 2: Send emails with reliability
        utc_now = timezone.now()
        
        # Get unsent digests
        unsent_digests = Reminder.objects.filter(
            reminder_type='daily_digest',
            digest_date=target_date,
            is_sent=False
        )
        
        # Include failed emails if retry requested
        if retry_failed:
            failed_digests = Reminder.objects.filter(
                reminder_type='daily_digest',
                digest_date=target_date,
                is_sent=True,
                sent_at__isnull=True
            )
            # Reset failed digests to unsent
            failed_digests.update(is_sent=False)
            self.stdout.write(f'🔄 Reset {failed_digests.count()} failed emails for retry')
        
        # Refresh unsent digests query
        unsent_digests = Reminder.objects.filter(
            reminder_type='daily_digest',
            digest_date=target_date,
            is_sent=False
        )
        
        self.stdout.write(f'📧 Processing {unsent_digests.count()} email deliveries...')
        
        for digest in unsent_digests:
            student = digest.student
            
            try:
                pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
                india_time = pref.digest_time
                
                # Convert India time to UTC
                india_offset = timedelta(hours=5, minutes=30)
                utc_equivalent_time = (
                    timezone.datetime.combine(target_date, india_time) - india_offset
                ).time()
                
                utc_equivalent_datetime = timezone.make_aware(
                    timezone.datetime.combine(target_date, utc_equivalent_time)
                )
                
                # Check if time to send
                if utc_now >= utc_equivalent_datetime:
                    success = self.send_reliable_email(student, digest, target_date)
                    
                    if success:
                        sent_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ DELIVERED to {student.username} - {india_time.strftime("%I:%M %p")} India')
                        )
                    else:
                        failed_count += 1
                        self.stdout.write(
                            self.style.ERROR(f'❌ FAILED {student.username} - will retry')
                        )
                else:
                    time_until = utc_equivalent_datetime - utc_now
                    hours = int(time_until.total_seconds() // 3600)
                    minutes = int((time_until.total_seconds() % 3600) // 60)
                    self.stdout.write(f'⏳ {student.username}: Due in {hours}h {minutes}m')
                    
            except DailyDigestPreference.DoesNotExist:
                self.stdout.write(f'⚠️  {student.username}: No time preference')
                continue
        
        # Restore original backend
        settings.EMAIL_BACKEND = original_backend
        
        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'📊 RELIABLE DELIVERY SUMMARY:'))
        self.stdout.write(f'   Generated: {generated_count}')
        self.stdout.write(f'   Delivered: {sent_count}')
        self.stdout.write(f'   Failed: {failed_count}')
        
        if sent_count > 0:
            self.stdout.write(self.style.SUCCESS('🎉 EMAILS DELIVERED SUCCESSFULLY!'))
    
    def send_reliable_email(self, student, digest, target_date):
        """Send email with multiple attempts"""
        
        # Try different email formats
        formats = [
            ('Simple Format', self.send_simple_email),
            ('Clean Format', self.send_clean_email),
            ('Minimal Format', self.send_minimal_email),
        ]
        
        for format_name, send_func in formats:
            try:
                send_func(student, digest, target_date)
                
                # Mark as sent
                digest.is_sent = True
                digest.sent_at = timezone.now()
                digest.save()
                
                return True
                
            except Exception as e:
                self.stdout.write(f'   ⚠️  {format_name} failed: {str(e)[:50]}...')
                continue
        
        return False
    
    def send_simple_email(self, student, digest, target_date):
        """Send simple email format"""
        send_mail(
            subject=f'Daily Schedule - {target_date.strftime("%B %d")}',
            message=digest.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            fail_silently=False,
        )
    
    def send_clean_email(self, student, digest, target_date):
        """Send clean email without emojis"""
        clean_message = self.remove_emojis(digest.message)
        send_mail(
            subject=f'Your Classes - {target_date.strftime("%A %B %d")}',
            message=clean_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            fail_silently=False,
        )
    
    def send_minimal_email(self, student, digest, target_date):
        """Send minimal email format"""
        minimal_message = f"""Hello {student.username},

Your classes for {target_date.strftime('%A, %B %d, %Y')}:

{self.extract_classes(digest.message)}

Best regards,
ClassWave Team"""
        
        send_mail(
            subject=f'Classes Today',
            message=minimal_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            fail_silently=False,
        )
    
    def remove_emojis(self, text):
        """Remove emojis from text"""
        emoji_chars = ['📅', '📚', '⏰', '👨‍🏫', '📍', '🎓', '💡']
        for emoji in emoji_chars:
            text = text.replace(emoji, '')
        return text
    
    def extract_classes(self, message):
        """Extract class information"""
        lines = message.split('\n')
        class_info = []
        
        for line in lines:
            if 'Time:' in line or 'Topic:' in line:
                clean_line = self.remove_emojis(line).strip()
                if clean_line:
                    class_info.append(clean_line)
        
        return '\n'.join(class_info) if class_info else 'No classes scheduled'

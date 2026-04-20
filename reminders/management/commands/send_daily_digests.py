from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from accounts.models import User
from reminders.tasks import create_daily_digest_for_student
from django.core.mail import send_mail
from django.conf import settings
from reminders.models import Reminder

class Command(BaseCommand):
    help = 'Generate and send daily digest emails for all students'

    def handle(self, *args, **kwargs):
        tomorrow = date.today() + timedelta(days=1)
        
        self.stdout.write(f'Generating daily digests for {tomorrow}...')
        
        # Get all students
        students = User.objects.filter(user_type='student')
        
        generated_count = 0
        sent_count = 0
        
        for student in students:
            # Generate digest for tomorrow
            digest = create_daily_digest_for_student(student.id, tomorrow)
            
            if digest:
                generated_count += 1
                
                # Send email immediately
                try:
                    send_mail(
                        subject=f'📅 Your Schedule for {tomorrow.strftime("%A, %B %d, %Y")}',
                        message=digest.message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[student.email],
                        fail_silently=False,
                    )
                    
                    # Mark as sent
                    digest.is_sent = True
                    digest.sent_at = timezone.now()
                    digest.save()
                    
                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Sent digest to {student.username} ({student.email})')
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Failed to send to {student.username}: {e}')
                    )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'📊 Summary:'))
        self.stdout.write(f'   Digests generated: {generated_count}')
        self.stdout.write(f'   Emails sent: {sent_count}')
        self.stdout.write(f'   Date: {tomorrow}')

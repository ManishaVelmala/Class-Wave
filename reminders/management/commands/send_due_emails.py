from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from reminders.models import Reminder
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Send all due emails immediately'

    def handle(self, *args, **options):
        now = timezone.now()
        
        self.stdout.write(f"🚀 Checking for due emails at {now.strftime('%H:%M:%S')}")
        
        # Find ONLY daily digests that should be sent now
        due_digests = Reminder.objects.filter(
            is_sent=False,
            reminder_time__lte=now,
            reminder_type='daily_digest'  # Only daily digests
        )
        
        if not due_digests.exists():
            self.stdout.write("ℹ️ No due emails found")
            return
        
        self.stdout.write(f"📧 Found {due_digests.count()} due emails")
        
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
                
                self.stdout.write(f"✅ Sent to {digest.student.username} ({digest.student.email})")
                sent_count += 1
                
            except Exception as e:
                self.stdout.write(f"❌ Failed to send to {digest.student.username}: {e}")
        
        self.stdout.write(
            self.style.SUCCESS(f'📧 Successfully sent {sent_count} emails')
        )
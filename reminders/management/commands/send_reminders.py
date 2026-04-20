from django.core.management.base import BaseCommand
from reminders.tasks import send_pending_reminders

class Command(BaseCommand):
    help = 'Send all pending reminders via email'

    def handle(self, *args, **kwargs):
        self.stdout.write('Checking for pending reminders...')
        
        count = send_pending_reminders()
        
        if count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Successfully sent {count} reminder emails!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('ℹ️  No pending reminders to send')
            )

from django.core.management.base import BaseCommand
from datetime import date
from reminders.models import Reminder

class Command(BaseCommand):
    help = 'Remove all past and future daily digests, keep only today\'s'

    def handle(self, *args, **options):
        today = date.today()
        
        self.stdout.write(f"🧹 Cleaning up digests - keeping only {today}")
        
        # Count existing digests
        total_digests = Reminder.objects.filter(reminder_type='daily_digest').count()
        today_digests = Reminder.objects.filter(
            reminder_type='daily_digest',
            digest_date=today
        ).count()
        
        self.stdout.write(f"   📊 Total digests: {total_digests}")
        self.stdout.write(f"   📅 Today's digests: {today_digests}")
        
        # Delete past and future digests
        past_future_digests = Reminder.objects.filter(
            reminder_type='daily_digest'
        ).exclude(digest_date=today)
        
        deleted_count = past_future_digests.count()
        past_future_digests.delete()
        
        self.stdout.write(f"   🗑️ Deleted {deleted_count} past/future digests")
        
        # Show remaining
        remaining = Reminder.objects.filter(reminder_type='daily_digest').count()
        self.stdout.write(f"   ✅ Remaining digests: {remaining}")
        
        if remaining == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ No classes today - notification bar will be empty')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Notification bar now shows only today\'s schedule')
            )
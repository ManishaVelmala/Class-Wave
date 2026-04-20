from django.core.management.base import BaseCommand
from reminders.models import Reminder

class Command(BaseCommand):
    help = 'Clean up existing update notifications from notification bar (they are now sent via email)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find all update type notifications
        update_notifications = Reminder.objects.filter(reminder_type='update')
        count = update_notifications.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ No update notifications found to clean up.')
            )
            return
        
        self.stdout.write(f"Found {count} update notifications to clean up:")
        
        # Show details
        for notification in update_notifications[:10]:  # Show first 10
            self.stdout.write(
                f"  - ID: {notification.id} | Student: {notification.student.username} | "
                f"Schedule: {notification.schedule.subject_name if notification.schedule else 'N/A'} | "
                f"Created: {notification.reminder_time.strftime('%Y-%m-%d %H:%M')}"
            )
        
        if count > 10:
            self.stdout.write(f"  ... and {count - 10} more")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\n🔍 DRY RUN: Would delete {count} update notifications. '
                    'Run without --dry-run to actually delete them.'
                )
            )
        else:
            # Actually delete them
            deleted_count, _ = update_notifications.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Successfully deleted {deleted_count} update notifications. '
                    'Update notifications are now sent via email only.'
                )
            )
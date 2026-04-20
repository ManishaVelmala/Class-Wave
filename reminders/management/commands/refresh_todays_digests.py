from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from accounts.models import User
from reminders.tasks import create_daily_digest_for_student

class Command(BaseCommand):
    help = 'Refresh today\'s daily digests for all students'

    def handle(self, *args, **options):
        today = date.today()
        
        self.stdout.write(f"🔄 Refreshing daily digests for {today}")
        
        students = User.objects.filter(user_type='student')
        refreshed_count = 0
        
        for student in students:
            self.stdout.write(f"   Refreshing digest for {student.username}...")
            
            # First, remove any existing digest for today
            from reminders.models import Reminder
            old_digests = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=today
            )
            
            if old_digests.exists():
                old_digests.delete()
                self.stdout.write(f"   🗑️ Removed old digest for {student.username}")
            
            # Generate fresh digest
            digest = create_daily_digest_for_student(student.id, today)
            
            if digest:
                # Mark as sent so it appears in notification bar
                digest.is_sent = True
                digest.save()
                refreshed_count += 1
                self.stdout.write(f"   ✅ Refreshed for {student.username}")
            else:
                self.stdout.write(f"   ℹ️ No classes today for {student.username} - no digest created")
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Successfully refreshed {refreshed_count} digests')
        )
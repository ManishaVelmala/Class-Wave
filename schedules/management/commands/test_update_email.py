from django.core.management.base import BaseCommand
from django.utils import timezone
from schedules.models import Schedule
from accounts.models import User

class Command(BaseCommand):
    help = 'Test schedule update email notifications'

    def add_arguments(self, parser):
        parser.add_argument('--schedule-id', type=int, help='Schedule ID to update')
        parser.add_argument('--new-topic', type=str, help='New topic for the schedule')

    def handle(self, *args, **options):
        schedule_id = options.get('schedule_id')
        new_topic = options.get('new_topic', 'Updated Test Topic')

        if schedule_id:
            try:
                schedule = Schedule.objects.get(id=schedule_id)
                old_topic = schedule.topic
                
                self.stdout.write(f"Updating schedule: {schedule.subject_name}")
                self.stdout.write(f"Old topic: {old_topic}")
                self.stdout.write(f"New topic: {new_topic}")
                self.stdout.write(f"Students enrolled: {schedule.students.count()}")
                
                # Update the schedule (this will trigger the signal)
                schedule.topic = new_topic
                schedule.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Schedule updated! Email notifications sent to {schedule.students.count()} students.'
                    )
                )
                
            except Schedule.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Schedule with ID {schedule_id} not found.')
                )
        else:
            # List available schedules
            schedules = Schedule.objects.all()[:10]
            self.stdout.write("Available schedules to test:")
            for schedule in schedules:
                self.stdout.write(
                    f"ID: {schedule.id} | {schedule.subject_name} | {schedule.topic} | Students: {schedule.students.count()}"
                )
            
            if schedules:
                self.stdout.write(f"\nTo test, run:")
                self.stdout.write(f"python manage.py test_update_email --schedule-id {schedules[0].id} --new-topic 'Test Update Topic'")
from django.core.management.base import BaseCommand
from accounts.models import User
from schedules.models import Schedule
from reminders.models import Reminder
from reminders.tasks import create_reminder_for_schedule

class Command(BaseCommand):
    help = 'Create reminders for students who are assigned to schedules but have no reminders'

    def handle(self, *args, **kwargs):
        students = User.objects.filter(user_type='student')
        
        total_created = 0
        
        for student in students:
            # Get all schedules assigned to this student
            assigned_schedules = student.assigned_schedules.all()
            
            self.stdout.write(f"\nChecking student: {student.username}")
            self.stdout.write(f"  Assigned schedules: {assigned_schedules.count()}")
            
            created_for_student = 0
            
            for schedule in assigned_schedules:
                # Check if reminder already exists
                existing_reminder = Reminder.objects.filter(
                    student=student,
                    schedule=schedule,
                    reminder_type='scheduled'
                ).first()
                
                if not existing_reminder:
                    # Create reminder
                    reminder = create_reminder_for_schedule(schedule.id, student.id)
                    if reminder:
                        created_for_student += 1
                        total_created += 1
            
            if created_for_student > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✅ Created {created_for_student} reminders for {student.username}"
                    )
                )
            else:
                self.stdout.write(f"  ℹ️  All reminders already exist for {student.username}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Total reminders created: {total_created}'
            )
        )

from django.core.management.base import BaseCommand
from schedules.models import Schedule
from accounts.models import StudentProfile

class Command(BaseCommand):
    help = 'Reassign students to schedules based on department and batch'

    def handle(self, *args, **kwargs):
        schedules = Schedule.objects.all()
        
        for schedule in schedules:
            if schedule.department:
                # Get all students in this department
                if schedule.batch:
                    student_profiles = StudentProfile.objects.filter(
                        department__iexact=schedule.department,
                        batch__iexact=schedule.batch
                    )
                else:
                    student_profiles = StudentProfile.objects.filter(
                        department__iexact=schedule.department
                    )
                
                students_to_add = [profile.user for profile in student_profiles]
                
                # Clear and reassign
                schedule.students.clear()
                schedule.students.add(*students_to_add)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Assigned {len(students_to_add)} students to "{schedule.subject_name}" '
                        f'(Dept: {schedule.department}, Batch: {schedule.batch or "All"})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Schedule "{schedule.subject_name}" has no department - skipped'
                    )
                )
        
        self.stdout.write(self.style.SUCCESS('\nReassignment complete!'))

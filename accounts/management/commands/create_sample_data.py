from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import User, StudentProfile, LecturerProfile
from schedules.models import Schedule

class Command(BaseCommand):
    help = 'Creates sample data for testing'

    def handle(self, *args, **kwargs):
        # Create lecturer
        lecturer, created = User.objects.get_or_create(
            username='lecturer1',
            defaults={
                'email': 'lecturer@example.com',
                'user_type': 'lecturer',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        if created:
            lecturer.set_password('password123')
            lecturer.save()
            LecturerProfile.objects.create(
                user=lecturer,
                department='Computer Science',
                designation='Professor',
                subjects='Data Structures, Web Development, Database Management'
            )
            self.stdout.write(self.style.SUCCESS('Created lecturer: lecturer1'))

        # Create students in Computer Science department
        students = []
        for i in range(1, 4):
            student, created = User.objects.get_or_create(
                username=f'student{i}',
                defaults={
                    'email': f'student{i}@example.com',
                    'user_type': 'student',
                    'first_name': f'Student{i}',
                    'last_name': 'Test'
                }
            )
            if created:
                student.set_password('password123')
                student.save()
                StudentProfile.objects.create(
                    user=student,
                    department='Computer Science',
                    batch='CS-2024',
                    roll_number=f'CS{i:03d}'
                )
                self.stdout.write(self.style.SUCCESS(f'Created student: student{i} (Computer Science)'))
            else:
                # Update existing student profile with department
                try:
                    profile = student.student_profile
                    if not profile.department:
                        profile.department = 'Computer Science'
                        profile.save()
                        self.stdout.write(self.style.SUCCESS(f'Updated student: student{i} with department'))
                except:
                    pass
            students.append(student)

        # Create sample schedules
        today = datetime.now().date()
        schedules_data = [
            {
                'subject_name': 'Data Structures',
                'topic': 'Binary Trees',
                'date': today + timedelta(days=1),
                'start_time': '09:00',
                'end_time': '10:30',
            },
            {
                'subject_name': 'Web Development',
                'topic': 'Django Framework',
                'date': today + timedelta(days=2),
                'start_time': '11:00',
                'end_time': '12:30',
            },
            {
                'subject_name': 'Database Management',
                'topic': 'SQL Queries',
                'date': today + timedelta(days=3),
                'start_time': '14:00',
                'end_time': '15:30',
            },
        ]

        for data in schedules_data:
            schedule, created = Schedule.objects.get_or_create(
                subject_name=data['subject_name'],
                topic=data['topic'],
                date=data['date'],
                defaults={
                    'lecturer': lecturer,
                    'department': 'Computer Science',
                    'start_time': data['start_time'],
                    'end_time': data['end_time'],
                    'batch': 'CS-2024'
                }
            )
            if created:
                # Students will be auto-assigned by department in the save method
                self.stdout.write(self.style.SUCCESS(f'Created schedule: {data["subject_name"]} (Auto-assigned to Computer Science students)'))

        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
        self.stdout.write(self.style.SUCCESS('Lecturer - username: lecturer1, password: password123'))
        self.stdout.write(self.style.SUCCESS('Students - username: student1/student2/student3, password: password123'))

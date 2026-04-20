import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User, StudentProfile
from schedules.models import Schedule

print("=" * 60)
print("SCHEDULE DIAGNOSTIC REPORT")
print("=" * 60)

# Check students
students = User.objects.filter(user_type='student')
print(f"\n📚 STUDENTS ({students.count()}):")
for student in students:
    if hasattr(student, 'student_profile'):
        profile = student.student_profile
        print(f"  - {student.username}")
        print(f"    Department: '{profile.department}'")
        print(f"    Batch: '{profile.batch}'")
        print(f"    Assigned schedules: {student.assigned_schedules.count()}")
    else:
        print(f"  - {student.username} (NO PROFILE)")

# Check lecturers
lecturers = User.objects.filter(user_type='lecturer')
print(f"\n👨‍🏫 LECTURERS ({lecturers.count()}):")
for lecturer in lecturers:
    if hasattr(lecturer, 'lecturer_profile'):
        profile = lecturer.lecturer_profile
        print(f"  - {lecturer.username} (Dept: {profile.department})")
    else:
        print(f"  - {lecturer.username}")

# Check schedules
schedules = Schedule.objects.all()
print(f"\n📅 SCHEDULES ({schedules.count()}):")
for schedule in schedules:
    print(f"  - {schedule.subject_name} ({schedule.date})")
    print(f"    Department: '{schedule.department}'")
    print(f"    Batch: '{schedule.batch}'")
    print(f"    Lecturer: {schedule.lecturer.username}")
    print(f"    Assigned students: {schedule.students.count()}")
    if schedule.students.count() > 0:
        for student in schedule.students.all():
            print(f"      • {student.username}")

print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("=" * 60)

if schedules.count() == 0:
    print("❌ No schedules found. Create schedules as a lecturer.")
elif students.count() == 0:
    print("❌ No students found. Register as a student.")
else:
    # Check for department mismatches
    for student in students:
        if hasattr(student, 'student_profile'):
            student_dept = student.student_profile.department
            matching_schedules = Schedule.objects.filter(department__iexact=student_dept)
            if matching_schedules.count() == 0:
                print(f"⚠️  Student '{student.username}' (Dept: '{student_dept}') has no matching schedules")
            else:
                assigned = student.assigned_schedules.count()
                if assigned == 0:
                    print(f"❌ Student '{student.username}' should have {matching_schedules.count()} schedules but has 0")
                    print(f"   Run: python manage.py reassign_students")
                else:
                    print(f"✅ Student '{student.username}' has {assigned} schedules assigned")

print("=" * 60)

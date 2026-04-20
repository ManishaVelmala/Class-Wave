import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from schedules.models import Schedule
from reminders.models import Reminder

print("=" * 60)
print("REMINDER DIAGNOSTIC REPORT")
print("=" * 60)

# Check students
students = User.objects.filter(user_type='student')
print(f"\n📚 STUDENTS ({students.count()}):")
for student in students:
    schedules_count = student.assigned_schedules.count()
    reminders_count = Reminder.objects.filter(student=student, reminder_type='scheduled').count()
    
    print(f"\n  👤 {student.username}")
    print(f"     Assigned schedules: {schedules_count}")
    print(f"     Reminders created: {reminders_count}")
    
    if schedules_count > reminders_count:
        print(f"     ⚠️  Missing {schedules_count - reminders_count} reminders!")
    elif reminders_count > 0:
        print(f"     ✅ All reminders created")

# Check total reminders
all_reminders = Reminder.objects.all()
print(f"\n📬 TOTAL REMINDERS: {all_reminders.count()}")
print(f"   Scheduled reminders: {Reminder.objects.filter(reminder_type='scheduled').count()}")
print(f"   Update notifications: {Reminder.objects.filter(reminder_type='update').count()}")
print(f"   Daily digests: {Reminder.objects.filter(reminder_type='daily_digest').count()}")

# Check sent vs pending
sent_count = Reminder.objects.filter(is_sent=True).count()
pending_count = Reminder.objects.filter(is_sent=False).count()
print(f"\n📊 STATUS:")
print(f"   Sent: {sent_count}")
print(f"   Pending: {pending_count}")

# Show sample reminders
print(f"\n📝 SAMPLE REMINDERS (first 5):")
sample_reminders = Reminder.objects.filter(reminder_type='scheduled')[:5]
for reminder in sample_reminders:
    print(f"\n   • {reminder.student.username} - {reminder.schedule.subject_name}")
    print(f"     Reminder time: {reminder.reminder_time}")
    print(f"     Sent: {'Yes' if reminder.is_sent else 'No'}")

print("\n" + "=" * 60)
print("SUMMARY:")
print("=" * 60)

total_schedules = Schedule.objects.count()
total_students = students.count()
expected_reminders = sum(s.assigned_schedules.count() for s in students)
actual_reminders = Reminder.objects.filter(reminder_type='scheduled').count()

print(f"Total schedules: {total_schedules}")
print(f"Total students: {total_students}")
print(f"Expected reminders: {expected_reminders}")
print(f"Actual reminders: {actual_reminders}")

if expected_reminders == actual_reminders:
    print("✅ All reminders are properly created!")
else:
    print(f"⚠️  Missing {expected_reminders - actual_reminders} reminders")
    print("   Run: python manage.py create_missing_reminders")

print("=" * 60)

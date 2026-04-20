from datetime import datetime, timedelta
from django.utils import timezone
from .models import Reminder
from schedules.models import Schedule
from accounts.models import User

def create_reminder_for_schedule(schedule_id, student_id, reminder_minutes=30):
    """
    Create a reminder for a student for a specific schedule.
    This can be called directly or scheduled via Celery.
    """
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        student = User.objects.get(id=student_id)
        
        # Calculate reminder time (timezone-aware)
        schedule_datetime = timezone.make_aware(datetime.combine(schedule.date, schedule.start_time))
        reminder_datetime = schedule_datetime - timedelta(minutes=reminder_minutes)
        
        # Create reminder message
        message = f"""
        Reminder: You have a class scheduled!
        
        Date: {schedule.date.strftime('%B %d, %Y')}
        Time: {schedule.start_time.strftime('%I:%M %p')} - {schedule.end_time.strftime('%I:%M %p')}
        Subject: {schedule.subject_name}
        Topic: {schedule.topic}
        Lecturer: {schedule.lecturer.get_full_name() or schedule.lecturer.username}
        """
        
        # Create or update reminder
        reminder, created = Reminder.objects.update_or_create(
            student=student,
            schedule=schedule,
            reminder_type='scheduled',
            defaults={
                'reminder_time': reminder_datetime,
                'message': message,
                'is_sent': False
            }
        )
        
        return reminder
    except (Schedule.DoesNotExist, User.DoesNotExist) as e:
        print(f"Error creating reminder: {e}")
        return None

def send_pending_reminders():
    """
    Send all pending reminders that are due.
    This should be called periodically via Celery Beat or cron.
    """
    from django.core.mail import send_mail
    from django.conf import settings
    
    now = timezone.now()
    # Send ONLY daily digests (not individual class reminders)
    pending_reminders = Reminder.objects.filter(
        is_sent=False,
        reminder_time__lte=now,
        reminder_type='daily_digest'  # Only daily digests
    )
    
    sent_count = 0
    for reminder in pending_reminders:
        try:
            # Prepare email subject for daily digest
            subject = f'📅 Your Schedule for {reminder.digest_date.strftime("%B %d, %Y")}'
            
            # Send email
            send_mail(
                subject=subject,
                message=reminder.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reminder.student.email],
                fail_silently=False,
            )
            
            # Mark as sent
            reminder.is_sent = True
            reminder.sent_at = now
            reminder.save()
            sent_count += 1
            
            print(f"✅ Email sent to {reminder.student.email}: {subject}")
            
        except Exception as e:
            print(f"⚠️ Failed to send email to {reminder.student.email}: {e}")
    
    return sent_count

# Update notifications are now handled directly in signals.py via email

def create_daily_digest_for_student(student_id, target_date):
    """
    Create a daily digest reminder showing all classes for a specific date.
    This combines all schedules for the day into ONE notification.
    """
    from datetime import datetime, time, timedelta, date
    from .models import Reminder, DailyDigestPreference
    
    try:
        # SAFEGUARD: Don't create digests for dates more than 1 day in the future
        today = date.today()
        if target_date > today + timedelta(days=1):
            print(f"Warning: Skipping digest creation for {target_date} (too far in future)")
            return None
        
        student = User.objects.get(id=student_id)
        
        # Get all schedules for this student on the target date
        schedules = Schedule.objects.filter(
            students=student,
            date=target_date
        ).order_by('start_time')
        
        if not schedules.exists():
            return None  # No classes today
        
        # Get student's digest preference
        try:
            pref = DailyDigestPreference.objects.get(student=student)
            digest_time = pref.digest_time  # This is now a TimeField object
            is_enabled = pref.is_enabled
        except DailyDigestPreference.DoesNotExist:
            digest_time = time(7, 0)  # Default: 7:00 AM
            is_enabled = True
        
        if not is_enabled:
            return None  # Student disabled daily digest
        
        # Calculate reminder datetime (timezone-aware)
        from django.utils import timezone as django_timezone
        
        # NEW: Store India time directly (no conversion to UTC)
        # We'll compare India times directly in the email sending logic
        india_datetime = datetime.combine(target_date, digest_time)
        
        # Convert India time to UTC for Django's timezone-aware storage
        # but we'll use India time for comparisons
        india_offset = timedelta(hours=5, minutes=30)
        utc_datetime = india_datetime - india_offset
        reminder_datetime = django_timezone.make_aware(utc_datetime)
        
        # Build the digest message
        message = f"""
📅 YOUR SCHEDULE FOR {target_date.strftime('%A, %B %d, %Y')}

You have {schedules.count()} class{'es' if schedules.count() > 1 else ''} today:

"""
        
        for idx, schedule in enumerate(schedules, 1):
            message += f"""
{idx}. {schedule.subject_name}
   📚 Topic: {schedule.topic}
   ⏰ Time: {schedule.start_time.strftime('%I:%M %p')} - {schedule.end_time.strftime('%I:%M %p')}
   👨‍🏫 Lecturer: {schedule.lecturer.get_full_name() or schedule.lecturer.username}
   📍 Department: {schedule.department}
"""
            if schedule.batch:
                message += f"   🎓 Batch: {schedule.batch}\n"
            message += "\n"
        
        message += """
💡 Tip: Check your calendar for more details!

Have a great day! 🎓
"""
        
        # Check if digest already exists for this date
        existing_digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=target_date
        ).first()
        
        if existing_digest:
            # Update existing digest
            existing_digest.message = message
            existing_digest.reminder_time = reminder_datetime
            existing_digest.is_sent = False
            existing_digest.save()
            return existing_digest
        else:
            # Create new digest
            digest = Reminder.objects.create(
                student=student,
                schedule=None,  # Not tied to a single schedule
                reminder_time=reminder_datetime,
                message=message,
                reminder_type='daily_digest',
                digest_date=target_date,
                is_sent=False
            )
            return digest
    
    except User.DoesNotExist:
        print(f"Error: Student {student_id} not found")
        return None

def generate_daily_digests_for_all_students():
    """
    Generate daily digest reminders for all students for tomorrow.
    This should be run daily (e.g., via Celery Beat at midnight).
    """
    from datetime import date, timedelta
    
    tomorrow = date.today() + timedelta(days=1)
    
    # Get all students
    students = User.objects.filter(user_type='student')
    
    created_count = 0
    for student in students:
        digest = create_daily_digest_for_student(student.id, tomorrow)
        if digest:
            created_count += 1
            print(f"✅ Created daily digest for {student.username} for {tomorrow}")
    
    print(f"\n📊 Total daily digests created: {created_count}")
    return created_count

# Celery tasks (optional - requires Celery setup)
try:
    from celery import shared_task
    
    @shared_task
    def create_reminder_task(schedule_id, student_id, reminder_minutes=30):
        return create_reminder_for_schedule(schedule_id, student_id, reminder_minutes)
    
    @shared_task
    def send_reminders_task():
        return send_pending_reminders()
    
    # Update notifications are handled directly via email in signals.py
    
    @shared_task
    def generate_daily_digests_task():
        """Celery task to generate daily digests for all students"""
        return generate_daily_digests_for_all_students()
except ImportError:
    # Celery not installed, tasks will run synchronously
    pass

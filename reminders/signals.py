from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from schedules.models import Schedule
from .models import Reminder

@receiver(pre_save, sender=Schedule)
def track_schedule_changes(sender, instance, **kwargs):
    """Track if schedule is being updated"""
    if instance.pk:  # Only for existing schedules
        try:
            old_schedule = Schedule.objects.get(pk=instance.pk)
            # Store old values for comparison
            instance._old_subject = old_schedule.subject_name
            instance._old_topic = old_schedule.topic
            instance._old_date = old_schedule.date
            instance._old_start_time = old_schedule.start_time
            instance._old_end_time = old_schedule.end_time
            instance._is_update = True
        except Schedule.DoesNotExist:
            instance._is_update = False
    else:
        instance._is_update = False

@receiver(post_save, sender=Schedule)
def notify_students_on_update(sender, instance, created, **kwargs):
    """Send update notifications to students when schedule is modified"""
    if not created and hasattr(instance, '_is_update') and instance._is_update:
        # Check if any important fields changed
        changes = []
        
        if hasattr(instance, '_old_subject') and instance._old_subject != instance.subject_name:
            changes.append(f"Subject: {instance._old_subject} → {instance.subject_name}")
        
        if hasattr(instance, '_old_topic') and instance._old_topic != instance.topic:
            changes.append(f"Topic: {instance._old_topic} → {instance.topic}")
        
        if hasattr(instance, '_old_date') and instance._old_date != instance.date:
            changes.append(f"Date: {instance._old_date} → {instance.date}")
        
        if hasattr(instance, '_old_start_time') and instance._old_start_time != instance.start_time:
            changes.append(f"Start Time: {instance._old_start_time} → {instance.start_time}")
        
        if hasattr(instance, '_old_end_time') and instance._old_end_time != instance.end_time:
            changes.append(f"End Time: {instance._old_end_time} → {instance.end_time}")
        
        # If there are changes, notify all assigned students
        if changes:
            for student in instance.students.all():
                create_update_notification(instance, student, changes)
                
                # Also refresh today's digest if the updated schedule is for today
                refresh_daily_digest_if_today(instance, student)

def refresh_daily_digest_if_today(schedule, student):
    """Refresh the daily digest if the updated schedule is for today"""
    from datetime import date
    from .tasks import create_daily_digest_for_student
    
    today = date.today()
    
    # Only refresh if the schedule is for today
    if schedule.date == today:
        print(f"🔄 Refreshing today's digest for {student.username} due to schedule update")
        
        # Regenerate today's digest with updated information
        updated_digest = create_daily_digest_for_student(student.id, today)
        
        if updated_digest:
            # Mark as sent so it appears in notification bar
            updated_digest.is_sent = True
            updated_digest.save()
            print(f"✅ Today's digest refreshed for {student.username}")

@receiver(post_delete, sender=Schedule)
def refresh_digest_on_schedule_delete(sender, instance, **kwargs):
    """Refresh daily digests when a schedule is deleted"""
    from datetime import date
    
    today = date.today()
    
    # Only refresh if the deleted schedule was for today
    if instance.date == today:
        print(f"🗑️ Schedule deleted for today: {instance.subject_name}")
        
        # Refresh digest for all students who were enrolled
        for student in instance.students.all():
            refresh_daily_digest_if_today(instance, student)

def create_update_notification(schedule, student, changes):
    """Send immediate email notification to student about schedule update"""
    from django.core.mail import send_mail
    from django.conf import settings
    
    change_text = "\n".join([f"  • {change}" for change in changes])
    
    message = f"""⚠️ SCHEDULE UPDATE ALERT ⚠️

A schedule you're enrolled in has been updated!

Subject: {schedule.subject_name}
Topic: {schedule.topic}
New Date: {schedule.date.strftime('%B %d, %Y')}
New Time: {schedule.start_time.strftime('%I:%M %p')} - {schedule.end_time.strftime('%I:%M %p')}
Lecturer: {schedule.lecturer.get_full_name() or schedule.lecturer.username}

Changes Made:
{change_text}

Please check your schedule and adjust your plans accordingly.

Best regards,
ClassWave Team 🔔"""
    
    # Send email immediately (no notification bar storage)
    try:
        send_mail(
            subject=f'📅 Schedule Update: {schedule.subject_name}',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            fail_silently=False,
        )
        print(f"✅ Update email sent to {student.email} for {schedule.subject_name}")
    except Exception as e:
        print(f"⚠️ Failed to send update email to {student.email}: {e}")
        # Fallback: create notification in database if email fails
        Reminder.objects.create(
            student=student,
            schedule=schedule,
            reminder_time=timezone.now(),
            message=message,
            reminder_type='update',
            is_sent=False
        )

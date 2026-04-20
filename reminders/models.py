from django.db import models
from accounts.models import User
from schedules.models import Schedule

class Reminder(models.Model):
    REMINDER_TYPE_CHOICES = (
        ('scheduled', 'Scheduled Reminder'),
        ('update', 'Update Notification'),
        ('daily_digest', 'Daily Schedule Digest'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='reminders', null=True, blank=True)
    reminder_time = models.DateTimeField()
    message = models.TextField()
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES, default='scheduled')
    is_sent = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # For daily digest
    digest_date = models.DateField(null=True, blank=True, help_text="Date for daily digest")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_reminder_type_display()} for {self.student.username}"

class DailyDigestPreference(models.Model):
    """Student's preference for daily digest timing"""
    
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='digest_preference')
    digest_time = models.TimeField(default='07:00', help_text='Choose any time for your daily digest email')
    is_enabled = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.student.username} - Daily Digest at {self.digest_time}"

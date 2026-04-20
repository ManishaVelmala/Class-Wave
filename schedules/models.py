from django.db import models
from accounts.models import User, StudentProfile

class Schedule(models.Model):
    DAY_ORDER_CHOICES = (
        ('1', 'Day 1'),
        ('2', 'Day 2'),
        ('3', 'Day 3'),
        ('4', 'Day 4'),
        ('5', 'Day 5'),
        ('6', 'Day 6'),
    )
    
    subject_name = models.CharField(max_length=200)
    topic = models.CharField(max_length=300)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedules')
    department = models.CharField(max_length=100, blank=True, null=True, help_text="Department for this schedule")
    day_order = models.CharField(max_length=1, choices=DAY_ORDER_CHOICES, blank=True, null=True, help_text="Day order (Day 1, Day 2, etc.)")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    batch = models.CharField(max_length=50, blank=True, null=True)
    students = models.ManyToManyField(User, related_name='assigned_schedules', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.subject_name} - {self.topic} ({self.date})"
    
    def save(self, *args, **kwargs):
        # Save the schedule first
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Auto-assign students from the same department
        if self.department:
            from accounts.models import StudentProfile
            
            # Get all students in this department
            if self.batch:
                # Filter by both department and batch
                student_profiles = StudentProfile.objects.filter(
                    department__iexact=self.department,
                    batch__iexact=self.batch
                )
            else:
                # Filter by department only
                student_profiles = StudentProfile.objects.filter(department__iexact=self.department)
            
            students_to_add = [profile.user for profile in student_profiles]
            
            # Clear existing students and add new ones
            self.students.clear()
            self.students.add(*students_to_add)
            
            # No individual reminders - students will get daily digest instead

class ReminderPreference(models.Model):
    REMINDER_CHOICES = (
        (10, '10 minutes before'),
        (30, '30 minutes before'),
        (60, '1 hour before'),
        (120, '2 hours before'),
        (1440, '1 day before'),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminder_preferences')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='reminder_preferences')
    reminder_time = models.IntegerField(choices=REMINDER_CHOICES, default=30)
    is_sent = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['student', 'schedule']
    
    def __str__(self):
        return f"{self.student.username} - {self.schedule.subject_name} ({self.get_reminder_time_display()})"

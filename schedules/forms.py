from django import forms
from .models import Schedule, ReminderPreference
from accounts.models import User

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['subject_name', 'topic', 'department', 'day_order', 'date', 'start_time', 'end_time', 'batch']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'subject_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Data Structures'}),
            'topic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Binary Trees'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Computer Science, MCA, BCA'}),
            'day_order': forms.Select(attrs={'class': 'form-control'}),
            'batch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional: e.g., 2024, Batch-A'}),
        }
        help_texts = {
            'department': '✅ All students in this department will automatically receive this schedule and reminders',
            'day_order': 'Optional: Select day order (Day 1, Day 2, etc.) if your college follows day order system',
            'batch': 'Optional: Further filter by specific batch within the department',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make department required
        self.fields['department'].required = True

class ReminderPreferenceForm(forms.ModelForm):
    class Meta:
        model = ReminderPreference
        fields = ['reminder_time']
        widgets = {
            'reminder_time': forms.Select(attrs={'class': 'form-control'}),
        }

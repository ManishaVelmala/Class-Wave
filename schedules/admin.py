from django.contrib import admin
from .models import Schedule, ReminderPreference

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['subject_name', 'topic', 'department', 'day_order', 'lecturer', 'date', 'start_time', 'end_time', 'batch']
    list_filter = ['date', 'day_order', 'department', 'lecturer', 'batch']
    search_fields = ['subject_name', 'topic', 'department', 'lecturer__username']
    filter_horizontal = ['students']

@admin.register(ReminderPreference)
class ReminderPreferenceAdmin(admin.ModelAdmin):
    list_display = ['student', 'schedule', 'reminder_time', 'is_sent']
    list_filter = ['reminder_time', 'is_sent']
    search_fields = ['student__username', 'schedule__subject_name']

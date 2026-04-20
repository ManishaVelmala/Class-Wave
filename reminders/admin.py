from django.contrib import admin
from .models import Reminder, DailyDigestPreference

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['student', 'get_schedule_or_digest', 'reminder_type', 'reminder_time', 'is_sent', 'is_read', 'sent_at']
    list_filter = ['reminder_type', 'is_sent', 'is_read', 'reminder_time', 'digest_date']
    search_fields = ['student__username', 'schedule__subject_name']
    readonly_fields = ['sent_at', 'created_at']
    
    def get_schedule_or_digest(self, obj):
        if obj.reminder_type == 'daily_digest':
            return f"Daily Digest - {obj.digest_date}"
        return obj.schedule.subject_name if obj.schedule else "N/A"
    get_schedule_or_digest.short_description = 'Schedule/Digest'

@admin.register(DailyDigestPreference)
class DailyDigestPreferenceAdmin(admin.ModelAdmin):
    list_display = ['student', 'digest_time', 'is_enabled']
    list_filter = ['digest_time', 'is_enabled']
    search_fields = ['student__username']

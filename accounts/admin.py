from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentProfile, LecturerProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'user_type', 'is_staff']
    list_filter = ['user_type', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone')}),
    )

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'batch', 'roll_number']
    list_filter = ['department', 'batch']
    search_fields = ['user__username', 'department', 'batch', 'roll_number']

@admin.register(LecturerProfile)
class LecturerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'designation', 'get_subjects_display']
    list_filter = ['department']
    search_fields = ['user__username', 'department', 'subjects']
    
    def get_subjects_display(self, obj):
        if obj.subjects:
            subjects = obj.get_subjects_list()
            if len(subjects) > 2:
                return f"{', '.join(subjects[:2])}... (+{len(subjects)-2} more)"
            return ', '.join(subjects)
        return "No subjects specified"
    get_subjects_display.short_description = 'Subjects'

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import Schedule, ReminderPreference
from .forms import ScheduleForm, ReminderPreferenceForm
from reminders.tasks import create_reminder_for_schedule

@login_required
def student_dashboard(request):
    if request.user.user_type != 'student' and not request.user.is_superuser:
        return redirect('lecturer_dashboard')
    
    # AUTO-GENERATE TODAY'S DIGEST FOR STUDENTS
    if request.user.user_type == 'student':
        from datetime import date
        from django.utils import timezone
        from reminders.models import Reminder
        from reminders.tasks import create_daily_digest_for_student
        
        today = date.today()
        
        try:
            # Check if today's digest exists
            todays_digest = Reminder.objects.filter(
                student=request.user,
                reminder_type='daily_digest',
                digest_date=today
            ).first()
            
            if not todays_digest:
                # Auto-generate today's digest
                digest = create_daily_digest_for_student(request.user.id, today)
                
                if digest:
                    # Don't send email immediately - respect time preferences
                    # Email will be sent by background service at student's preferred time
                    pass
        except Exception:
            pass  # Continue if auto-generation fails
    
    # Admin can see all schedules, students see their own
    if request.user.is_superuser:
        schedules = Schedule.objects.all().order_by('date', 'start_time')
        department = "Admin - All Departments"
    else:
        # Get schedules assigned to this student (either directly or by department)
        schedules = Schedule.objects.filter(students=request.user).order_by('date', 'start_time')
        
        # Get student's department
        try:
            student_profile = request.user.student_profile
            department = student_profile.department
        except:
            department = None
    
    context = {
        'schedules': schedules,
        'department': department,
    }
    return render(request, 'schedules/student_dashboard.html', context)

@login_required
def lecturer_dashboard(request):
    if request.user.user_type != 'lecturer' and not request.user.is_superuser:
        return redirect('student_dashboard')
    
    # Admin can see all schedules, lecturers see their own
    if request.user.is_superuser:
        schedules = Schedule.objects.all().order_by('date', 'start_time')
    else:
        schedules = Schedule.objects.filter(lecturer=request.user).order_by('date', 'start_time')
    
    return render(request, 'schedules/lecturer_dashboard.html', {'schedules': schedules})

@login_required
def schedule_list(request):
    if request.user.is_superuser:
        # Admin can see all schedules
        schedules = Schedule.objects.all().order_by('date', 'start_time')
    elif request.user.user_type == 'student':
        schedules = Schedule.objects.filter(students=request.user).order_by('date', 'start_time')
    else:
        schedules = Schedule.objects.filter(lecturer=request.user).order_by('date', 'start_time')
    return render(request, 'schedules/schedule_list.html', {'schedules': schedules})

@login_required
def schedule_calendar(request):
    if request.user.is_superuser:
        # Admin can see all schedules
        schedules = Schedule.objects.all()
    elif request.user.user_type == 'student':
        schedules = Schedule.objects.filter(students=request.user)
    else:
        schedules = Schedule.objects.filter(lecturer=request.user)
    return render(request, 'schedules/schedule_calendar.html', {'schedules': schedules})

@login_required
def schedule_calendar_data(request):
    if request.user.is_superuser:
        # Admin can see all schedules
        schedules = Schedule.objects.all()
    elif request.user.user_type == 'student':
        schedules = Schedule.objects.filter(students=request.user)
    else:
        schedules = Schedule.objects.filter(lecturer=request.user)
    
    events = []
    for schedule in schedules:
        events.append({
            'title': f"{schedule.subject_name} - {schedule.topic}",
            'start': f"{schedule.date}T{schedule.start_time}",
            'end': f"{schedule.date}T{schedule.end_time}",
            'url': f"/schedules/{schedule.id}/",
        })
    
    return JsonResponse(events, safe=False)

@login_required
def create_schedule(request):
    if request.user.user_type != 'lecturer':
        messages.error(request, 'Only lecturers can create schedules.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.lecturer = request.user
            # Auto-fill department from lecturer's profile if not provided
            if not schedule.department and hasattr(request.user, 'lecturer_profile'):
                schedule.department = request.user.lecturer_profile.department
            schedule.save()
            # Students are automatically assigned in the model's save method
            
            messages.success(request, f'Schedule created successfully! Assigned to all students in {schedule.department} department.')
            return redirect('lecturer_dashboard')
    else:
        form = ScheduleForm()
        # Pre-fill department from lecturer's profile
        if hasattr(request.user, 'lecturer_profile') and request.user.lecturer_profile.department:
            form.initial['department'] = request.user.lecturer_profile.department
    return render(request, 'schedules/schedule_form.html', {'form': form, 'action': 'Create'})

@login_required
def edit_schedule(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, lecturer=request.user)
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule updated successfully!')
            return redirect('lecturer_dashboard')
    else:
        form = ScheduleForm(instance=schedule)
    return render(request, 'schedules/schedule_form.html', {'form': form, 'action': 'Edit'})

@login_required
def delete_schedule(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, lecturer=request.user)
    
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Schedule deleted successfully!')
        return redirect('lecturer_dashboard')
    
    return render(request, 'schedules/schedule_confirm_delete.html', {'schedule': schedule})

@login_required
def schedule_detail(request, pk):
    if request.user.is_superuser:
        # Admin can see any schedule
        schedule = get_object_or_404(Schedule, pk=pk)
    elif request.user.user_type == 'student':
        schedule = get_object_or_404(Schedule, pk=pk, students=request.user)
    else:
        schedule = get_object_or_404(Schedule, pk=pk, lecturer=request.user)
    
    return render(request, 'schedules/schedule_detail.html', {'schedule': schedule})

@login_required
def set_reminder(request, schedule_id):
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can set reminders.')
        return redirect('dashboard')
    
    schedule = get_object_or_404(Schedule, pk=schedule_id, students=request.user)
    
    if request.method == 'POST':
        form = ReminderPreferenceForm(request.POST)
        if form.is_valid():
            reminder_pref, created = ReminderPreference.objects.get_or_create(
                student=request.user,
                schedule=schedule
            )
            reminder_pref.reminder_time = form.cleaned_data['reminder_time']
            reminder_pref.save()
            
            # Create/update reminder
            create_reminder_for_schedule(schedule.id, request.user.id, reminder_pref.reminder_time)
            
            messages.success(request, 'Reminder preference saved!')
            return redirect('schedule_detail', pk=schedule_id)
    else:
        try:
            reminder_pref = ReminderPreference.objects.get(student=request.user, schedule=schedule)
            form = ReminderPreferenceForm(instance=reminder_pref)
        except ReminderPreference.DoesNotExist:
            form = ReminderPreferenceForm()
    
    return render(request, 'schedules/set_reminder.html', {'form': form, 'schedule': schedule})

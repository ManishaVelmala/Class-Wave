from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentRegistrationForm, LecturerRegistrationForm, ProfileUpdateForm

def home(request):
    return render(request, 'home.html')

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Auto-assign existing schedules to this student
            if hasattr(user, 'student_profile'):
                from schedules.models import Schedule
                from reminders.tasks import create_reminder_for_schedule
                student_profile = user.student_profile
                
                # Find all schedules matching this student's department and batch
                if student_profile.batch:
                    matching_schedules = Schedule.objects.filter(
                        department__iexact=student_profile.department,
                        batch__iexact=student_profile.batch
                    )
                else:
                    matching_schedules = Schedule.objects.filter(
                        department__iexact=student_profile.department
                    )
                
                # Assign student to all matching schedules (no individual reminders)
                for schedule in matching_schedules:
                    schedule.students.add(user)
                
                if matching_schedules.count() > 0:
                    messages.success(request, f'Registration successful! You have been assigned to {matching_schedules.count()} schedules. Enable daily digest to get all classes in one email!')
                else:
                    messages.success(request, 'Registration successful!')
            else:
                messages.success(request, 'Registration successful!')
            
            # Login user after registration
            login(request, user)
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'accounts/register_student.html', {'form': form})

def register_lecturer(request):
    if request.method == 'POST':
        form = LecturerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Login user after registration
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = LecturerRegistrationForm()
    return render(request, 'accounts/register_lecturer.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.is_superuser:
        # Admin can choose - default to lecturer dashboard to see all schedules
        return redirect('lecturer_dashboard')
    elif request.user.user_type == 'student':
        return redirect('student_dashboard')
    else:
        return redirect('lecturer_dashboard')

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        
        # Handle profile-specific forms
        profile_form = None
        if request.user.user_type == 'lecturer' and hasattr(request.user, 'lecturer_profile'):
            from .forms import LecturerProfileUpdateForm
            profile_form = LecturerProfileUpdateForm(request.POST, instance=request.user.lecturer_profile)
        elif request.user.user_type == 'student' and hasattr(request.user, 'student_profile'):
            from .forms import StudentProfileUpdateForm
            profile_form = StudentProfileUpdateForm(request.POST, instance=request.user.student_profile)
        
        if form.is_valid() and (profile_form is None or profile_form.is_valid()):
            form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
        profile_form = None
        if request.user.user_type == 'lecturer' and hasattr(request.user, 'lecturer_profile'):
            from .forms import LecturerProfileUpdateForm
            profile_form = LecturerProfileUpdateForm(instance=request.user.lecturer_profile)
        elif request.user.user_type == 'student' and hasattr(request.user, 'student_profile'):
            from .forms import StudentProfileUpdateForm
            profile_form = StudentProfileUpdateForm(instance=request.user.student_profile)
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile_form': profile_form
    })

# Removed custom login view - using Django's default LoginView
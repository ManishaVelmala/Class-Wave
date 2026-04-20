from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import models
from django.db.models import Q
from .models import Reminder, DailyDigestPreference

@login_required
def notifications(request):
    """View all notifications for the logged-in student"""
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can view notifications.')
        return redirect('dashboard')
    
    from django.utils import timezone
    from datetime import timedelta, date
    from .tasks import create_daily_digest_for_student
    
    # Get current time and date
    now = timezone.now()
    today = date.today()
    
    # AUTO-GENERATE TODAY'S DIGEST IF IT DOESN'T EXIST
    try:
        todays_digest = Reminder.objects.filter(
            student=request.user,
            reminder_type='daily_digest',
            digest_date=today
        ).first()
        
        if not todays_digest:
            # Generate today's digest automatically
            digest = create_daily_digest_for_student(request.user.id, today)
            
            if digest:
                # Don't send email immediately - respect time preferences
                # Email will be sent by background service at student's preferred time
                # Digest is created and ready for notification bar display
                messages.success(request, f'📅 Today\'s schedule digest has been generated! Email will be sent at your preferred time.')
                pass
    except Exception:
        # If auto-generation fails, continue normally
        pass
    
    # Show ONLY today's digest - no past or future schedules
    all_notifications = Reminder.objects.filter(
        student=request.user,
        reminder_type='daily_digest',
        digest_date=today,  # Only today's digest
        is_sent=True  # Only sent digests (appear in notification bar)
    )
    
    unread_notifications = all_notifications.filter(is_read=False)
    
    context = {
        'notifications': all_notifications,
        'unread_count': unread_notifications.count(),
    }
    
    return render(request, 'reminders/notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    if request.user.user_type != 'student':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    notification = get_object_or_404(Reminder, id=notification_id, student=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications')

@login_required
def mark_all_read(request):
    """Mark all notifications as read"""
    if request.user.user_type != 'student':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    Reminder.objects.filter(student=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    
    return redirect('notifications')

@login_required
def unread_count(request):
    """Get unread notification count (for AJAX)"""
    if request.user.user_type != 'student':
        return JsonResponse({'count': 0})
    
    # FIXED: Only count notifications that were actually SENT via email
    # Don't count "due" digests that haven't been sent yet
    # This respects time preferences - badge only appears when email is sent
    count = Reminder.objects.filter(
        student=request.user,
        is_read=False,
        reminder_type='daily_digest',
        is_sent=True  # Only count digests that were actually sent via email
    ).count()
    
    return JsonResponse({'count': count})


@login_required
def digest_preferences(request):
    """Manage daily digest preferences"""
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can manage digest preferences.')
        return redirect('dashboard')
    
    from datetime import time
    
    # Get or create preference
    pref, created = DailyDigestPreference.objects.get_or_create(
        student=request.user,
        defaults={'digest_time': time(7, 0), 'is_enabled': True}  # 7:00 AM default
    )
    
    if request.method == 'POST':
        digest_time_str = request.POST.get('digest_time')
        is_enabled = request.POST.get('is_enabled') == 'on'
        
        try:
            # Parse the time string (format: HH:MM)
            hour, minute = map(int, digest_time_str.split(':'))
            digest_time = time(hour, minute)
            
            pref.digest_time = digest_time
            pref.is_enabled = is_enabled
            pref.save()
            
            # Format time for display
            time_display = digest_time.strftime('%I:%M %p')
            messages.success(request, f'Daily digest preferences updated! You will receive emails at {time_display}.')
            return redirect('digest_preferences')
            
        except (ValueError, AttributeError):
            messages.error(request, 'Invalid time format. Please select a valid time.')
    
    context = {
        'preference': pref,
    }
    return render(request, 'reminders/digest_preferences.html', context)

@login_required
def generate_my_digest(request):
    """Manually generate today's digest for testing"""
    if request.user.user_type != 'student':
        return JsonResponse({'error': 'Only students can generate digests'}, status=403)
    
    from datetime import date
    from .tasks import create_daily_digest_for_student
    
    today = date.today()
    digest = create_daily_digest_for_student(request.user.id, today)
    
    if digest:
        messages.success(request, f'Daily digest generated! Check your notifications.')
        return redirect('notifications')
    else:
        messages.info(request, 'No classes scheduled for today.')
        return redirect('notifications')

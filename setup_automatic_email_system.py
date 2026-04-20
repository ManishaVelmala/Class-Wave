#!/usr/bin/env python3
"""
Setup automatic email system that works without manual intervention
"""

import os
import sys
import django
from datetime import date, time, datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def setup_automatic_system():
    """Setup the automatic email system"""
    
    print("🔧 SETTING UP AUTOMATIC EMAIL SYSTEM")
    print("=" * 45)
    print("   • No manual services to run")
    print("   • Uses existing Windows Task Scheduler")
    print("   • Handles India timezone automatically")
    
    # Create improved batch file for Task Scheduler
    batch_content = '''@echo off
echo [%date% %time%] Running ClassWave Email Service...
cd /d "%~dp0"
python manage.py send_real_daily_digests
echo [%date% %time%] Email service completed
echo.
'''
    
    try:
        with open('automatic_email_service.bat', 'w') as f:
            f.write(batch_content)
        print("✅ Created automatic_email_service.bat")
    except Exception as e:
        print(f"❌ Error creating batch file: {e}")
    
    # Create PowerShell script to setup Task Scheduler
    powershell_content = '''# PowerShell script to setup automatic email system
$TaskName = "ClassWave-Email-Service"
$ScriptPath = Get-Location
$BatchFile = Join-Path $ScriptPath "automatic_email_service.bat"

Write-Host "Setting up ClassWave Email Service..."
Write-Host "Batch file: $BatchFile"

# Delete existing task if it exists
try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed existing task"
} catch {
    Write-Host "No existing task to remove"
}

# Create new task that runs every 30 minutes
$Action = New-ScheduledTaskAction -Execute $BatchFile
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration (New-TimeSpan -Days 365)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the task
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "ClassWave automatic email service - checks every 30 minutes"

Write-Host "✅ Task scheduled successfully!"
Write-Host "   • Task name: $TaskName"
Write-Host "   • Runs every: 30 minutes"
Write-Host "   • Handles India timezone automatically"
Write-Host ""
Write-Host "🎯 SYSTEM IS NOW FULLY AUTOMATIC!"
Write-Host "   Students will receive emails at their preferred India times"
Write-Host "   No manual intervention required"
'''
    
    try:
        with open('setup_automatic_emails.ps1', 'w') as f:
            f.write(powershell_content)
        print("✅ Created setup_automatic_emails.ps1")
    except Exception as e:
        print(f"❌ Error creating PowerShell script: {e}")

def test_timezone_conversion():
    """Test the timezone conversion logic"""
    
    print(f"\n🧪 TESTING TIMEZONE CONVERSION")
    print("=" * 35)
    
    # Test conversion for common times
    test_times = [
        time(9, 0),   # 9:00 AM India
        time(14, 30), # 2:30 PM India  
        time(21, 18), # 9:18 PM India
        time(23, 55), # 11:55 PM India
    ]
    
    today = date.today()
    
    for india_time in test_times:
        # Convert India time to UTC
        india_offset = timedelta(hours=5, minutes=30)
        india_datetime = datetime.combine(today, india_time)
        utc_datetime = india_datetime - india_offset
        utc_time = utc_datetime.time()
        
        print(f"   {india_time.strftime('%I:%M %p')} India → {utc_time.strftime('%I:%M %p')} UTC")

def show_current_status():
    """Show current status of the system"""
    
    print(f"\n📊 CURRENT SYSTEM STATUS")
    print("=" * 30)
    
    utc_now = timezone.now()
    india_offset = timedelta(hours=5, minutes=30)
    india_now = utc_now + india_offset
    
    print(f"🕐 Current UTC time: {utc_now.time().strftime('%I:%M %p')}")
    print(f"🇮🇳 Current India time: {india_now.time().strftime('%I:%M %p')}")
    
    # Check students with preferences
    students_with_prefs = DailyDigestPreference.objects.filter(is_enabled=True).count()
    print(f"👥 Students with preferences: {students_with_prefs}")
    
    # Check today's digests
    today = date.today()
    total_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today
    ).count()
    
    sent_digests = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today,
        is_sent=True
    ).count()
    
    print(f"📝 Today's digests: {total_digests}")
    print(f"📧 Emails sent: {sent_digests}")
    print(f"⏳ Pending: {total_digests - sent_digests}")

if __name__ == "__main__":
    setup_automatic_system()
    test_timezone_conversion()
    show_current_status()
    
    print(f"\n" + "=" * 50)
    print("🎯 SETUP COMPLETE!")
    print("=" * 20)
    print("1. Run: setup_automatic_emails.ps1 (as Administrator)")
    print("2. That's it! System will work automatically")
    print("")
    print("✅ Benefits:")
    print("   • No manual services to run")
    print("   • Uses existing Windows Task Scheduler")
    print("   • Checks every 30 minutes automatically")
    print("   • Handles India timezone conversion")
    print("   • Students get emails at preferred times")
    print("")
    print("🎉 You never need to run anything manually again!")
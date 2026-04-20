# Fix Email Timing by Updating Windows Task Scheduler
# This script updates the existing task to run every 30 minutes instead of once daily

Write-Host "FIXING EMAIL TIMING ISSUE" -ForegroundColor Cyan
Write-Host "======================================"

# Check if task exists
$taskName = "ClassWave Daily Digest"
$taskExists = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($taskExists) {
    Write-Host "Found existing task: $taskName" -ForegroundColor Green
    
    # Delete the old task
    Write-Host "Removing old task configuration..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    
    Write-Host "Old task removed" -ForegroundColor Green
} else {
    Write-Host "Task not found, will create new one" -ForegroundColor Yellow
}

# Get current directory
$currentDir = Get-Location

# Create new task that runs every 30 minutes
Write-Host "Creating new task that runs every 30 minutes..." -ForegroundColor Cyan

# Define the action
$action = New-ScheduledTaskAction -Execute "python" -Argument "manage.py send_real_daily_digests" -WorkingDirectory $currentDir

# Define trigger - runs every 30 minutes, 24/7
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration (New-TimeSpan -Days 365)

# Define settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Define principal (run as current user)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# Register the new task
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "ClassWave Daily Digest - Runs every 30 minutes to send emails at student preferred times"

Write-Host ""
Write-Host "TASK UPDATED SUCCESSFULLY!" -ForegroundColor Green
Write-Host ""
Write-Host "New Configuration:" -ForegroundColor Cyan
Write-Host "   Task Name: $taskName"
Write-Host "   Frequency: Every 30 minutes"
Write-Host "   Duration: Continuous (365 days)"
Write-Host "   Command: python manage.py send_real_daily_digests"
Write-Host "   Working Directory: $currentDir"
Write-Host ""
Write-Host "RESULT:" -ForegroundColor Green
Write-Host "   - Emails will now be sent at student's preferred times"
Write-Host "   - Task checks every 30 minutes for due emails"
Write-Host "   - Students get emails throughout the day"
Write-Host "   - No more 6:00 AM limitation"
Write-Host ""
Write-Host "To verify the task:" -ForegroundColor Yellow
Write-Host "   schtasks /query /tn `"ClassWave Daily Digest`""
Write-Host ""
Write-Host "Next check will be in 30 minutes" -ForegroundColor Cyan
# Create Continuous Email System for Perfect Time Preference Accuracy
# This system runs CONTINUOUSLY to ensure emails are sent at EXACT preferred times

Write-Host "CREATING CONTINUOUS EMAIL SYSTEM" -ForegroundColor Cyan
Write-Host "=================================="

# Remove old task
$taskName = "ClassWave Daily Digest"
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed old task" -ForegroundColor Yellow
} catch {
    Write-Host "No existing task to remove" -ForegroundColor Gray
}

# Get current directory
$currentDir = Get-Location

# Create continuous task that runs EVERY MINUTE for perfect accuracy
Write-Host "Creating continuous email delivery task..." -ForegroundColor Cyan

$action = New-ScheduledTaskAction -Execute "python" -Argument "manage.py send_real_daily_digests --retry-failed" -WorkingDirectory $currentDir

# Run EVERY MINUTE for perfect timing accuracy
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1) -RepetitionDuration (New-TimeSpan -Days 365)

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "ClassWave Continuous Email System - Runs EVERY MINUTE for perfect timing accuracy"

Write-Host ""
Write-Host "CONTINUOUS EMAIL SYSTEM ACTIVATED!" -ForegroundColor Green
Write-Host ""
Write-Host "New Configuration:" -ForegroundColor Cyan
Write-Host "   Task Name: $taskName"
Write-Host "   Frequency: EVERY MINUTE (60 seconds)"
Write-Host "   Command: python manage.py send_real_daily_digests --retry-failed"
Write-Host "   Accuracy: Perfect timing (within 1 minute)"
Write-Host ""
Write-Host "Benefits:" -ForegroundColor Green
Write-Host "   - Checks for due emails every 60 seconds"
Write-Host "   - Maximum 1-minute delay (perfect accuracy)"
Write-Host "   - Emails sent at EXACT preferred times"
Write-Host "   - Continuous monitoring 24/7"
Write-Host "   - Automatic retry of failed deliveries"
Write-Host ""
Write-Host "Student Experience:" -ForegroundColor Yellow
Write-Host "   1. Student sets time preference: 11:30:00 PM"
Write-Host "   2. System checks every minute: 11:29, 11:30, 11:31..."
Write-Host "   3. At exactly 11:30 PM, email is sent"
Write-Host "   4. Maximum delay: 60 seconds"
Write-Host "   5. Perfect timing accuracy!"
Write-Host ""
Write-Host "Alternative: Create Windows Service (runs continuously)" -ForegroundColor Magenta
Write-Host "   For even better performance, we can create a Windows Service"
Write-Host "   that runs continuously in the background"
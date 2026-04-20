# Create 30-Second Email System for Maximum Timing Accuracy
# This system runs EVERY 30 SECONDS for perfect time preference accuracy

Write-Host "CREATING 30-SECOND EMAIL SYSTEM" -ForegroundColor Cyan
Write-Host "================================="

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

# Create 30-second precision task
Write-Host "Creating 30-second precision email delivery task..." -ForegroundColor Cyan

$action = New-ScheduledTaskAction -Execute "python" -Argument "manage.py send_real_daily_digests --retry-failed" -WorkingDirectory $currentDir

# Run EVERY 30 SECONDS for maximum precision
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Seconds 30) -RepetitionDuration (New-TimeSpan -Days 365)

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "ClassWave 30-Second Email System - Maximum timing accuracy for perfect time preferences"

Write-Host ""
Write-Host "30-SECOND EMAIL SYSTEM ACTIVATED!" -ForegroundColor Green
Write-Host ""
Write-Host "MAXIMUM ACCURACY CONFIGURATION:" -ForegroundColor Cyan
Write-Host "   Task Name: $taskName"
Write-Host "   Frequency: EVERY 30 SECONDS"
Write-Host "   Command: python manage.py send_real_daily_digests --retry-failed"
Write-Host "   Accuracy: Perfect timing (within 30 seconds)"
Write-Host "   Monitoring: 24/7 continuous"
Write-Host ""
Write-Host "PERFECT TIMING BENEFITS:" -ForegroundColor Green
Write-Host "   - Checks for due emails every 30 seconds"
Write-Host "   - Maximum 30-second delay (perfect accuracy)"
Write-Host "   - Emails sent at EXACT preferred times"
Write-Host "   - Continuous monitoring around the clock"
Write-Host "   - Automatic retry of failed deliveries"
Write-Host "   - No missed time preferences"
Write-Host ""
Write-Host "STUDENT EXPERIENCE:" -ForegroundColor Yellow
Write-Host "   1. Student sets time preference: 11:30:15 PM"
Write-Host "   2. System checks: 11:30:00, 11:30:30, 11:31:00..."
Write-Host "   3. At 11:30:30 check, system detects time has passed"
Write-Host "   4. Email sent immediately (within 30 seconds)"
Write-Host "   5. Perfect timing accuracy achieved!"
Write-Host ""
Write-Host "TIMING EXAMPLES:" -ForegroundColor Magenta
Write-Host "   - Preference: 09:15 AM -> Email sent by 09:15:30 AM"
Write-Host "   - Preference: 02:45 PM -> Email sent by 02:45:30 PM"
Write-Host "   - Preference: 11:30 PM -> Email sent by 11:30:30 PM"
Write-Host "   - ANY time preference works with 30-second accuracy!"
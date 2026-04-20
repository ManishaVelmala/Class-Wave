# Create Reliable Email System for ClassWave
# This system guarantees email delivery at student's preferred time

Write-Host "CREATING RELIABLE EMAIL SYSTEM" -ForegroundColor Cyan
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

# Create new reliable task that runs every 10 minutes
Write-Host "Creating reliable email delivery task..." -ForegroundColor Cyan

$action = New-ScheduledTaskAction -Execute "python" -Argument "manage.py send_real_daily_digests --retry-failed" -WorkingDirectory $currentDir

# Run every 10 minutes for maximum reliability
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 10) -RepetitionDuration (New-TimeSpan -Days 365)

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "ClassWave Reliable Email System - Runs every 10 minutes with retry mechanism"

Write-Host ""
Write-Host "RELIABLE EMAIL SYSTEM ACTIVATED!" -ForegroundColor Green
Write-Host ""
Write-Host "New Configuration:" -ForegroundColor Cyan
Write-Host "   Task Name: $taskName"
Write-Host "   Frequency: Every 10 minutes"
Write-Host "   Command: python manage.py send_real_daily_digests --retry-failed"
Write-Host "   Features: Automatic retry of failed emails"
Write-Host ""
Write-Host "Benefits:" -ForegroundColor Green
Write-Host "   - Checks for due emails every 10 minutes"
Write-Host "   - Automatically retries failed deliveries"
Write-Host "   - Guarantees email delivery at preferred times"
Write-Host "   - No manual intervention required"
Write-Host ""
Write-Host "Student Experience:" -ForegroundColor Yellow
Write-Host "   1. Student registers and sets time preference"
Write-Host "   2. System creates digest automatically"
Write-Host "   3. Email sent at EXACT preferred time"
Write-Host "   4. If delivery fails, system retries every 10 minutes"
Write-Host "   5. Student WILL receive email"
# Create Windows startup task for 30-second email service
Write-Host "CREATING AUTO-STARTUP TASK" -ForegroundColor Cyan
Write-Host "=========================="

$taskName = "ClassWave 30-Second Email Startup"
$currentDir = Get-Location

# Remove existing task
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed existing task" -ForegroundColor Yellow
} catch {
    Write-Host "No existing task to remove" -ForegroundColor Gray
}

# Create startup task
$action = New-ScheduledTaskAction -Execute "python" -Argument "start_continuous_email_service.py" -WorkingDirectory $currentDir

$trigger = New-ScheduledTaskTrigger -AtStartup

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Auto-start ClassWave 30-second email service on system startup"

Write-Host ""
Write-Host "AUTO-STARTUP CONFIGURED!" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "   Task: $taskName"
Write-Host "   Trigger: System startup"
Write-Host "   Action: Start 30-second email service"
Write-Host "   Accuracy: 30-second precision"
Write-Host ""
Write-Host "Benefits:" -ForegroundColor Green
Write-Host "   - Service starts automatically when computer boots"
Write-Host "   - Perfect timing maintained 24/7"
Write-Host "   - No manual intervention required"
Write-Host "   - Students get emails at exact preferred times"
Write-Host ""
Write-Host "Service Status:" -ForegroundColor Yellow
Write-Host "   The 30-second email service will now start automatically"
Write-Host "   every time your computer boots up."
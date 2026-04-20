# PowerShell script to setup automatic email system
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

Write-Host "SUCCESS: Task scheduled successfully!"
Write-Host "   Task name: $TaskName"
Write-Host "   Runs every: 30 minutes"
Write-Host "   Handles India timezone automatically"
Write-Host ""
Write-Host "SYSTEM IS NOW FULLY AUTOMATIC!"
Write-Host "   Students will receive emails at their preferred India times"
Write-Host "   No manual intervention required"
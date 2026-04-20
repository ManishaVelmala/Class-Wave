# PowerShell script to set up automatic email service
# This will create a Windows Task that starts the email service automatically

Write-Host "🚀 SETTING UP AUTOMATIC EMAIL SERVICE" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Get current directory
$currentDir = Get-Location
$pythonScript = Join-Path $currentDir "start_continuous_email_service.py"
$pythonExe = (Get-Command python).Source

Write-Host "📍 Current directory: $currentDir" -ForegroundColor Yellow
Write-Host "🐍 Python executable: $pythonExe" -ForegroundColor Yellow
Write-Host "📧 Email service script: $pythonScript" -ForegroundColor Yellow

# Check if script exists
if (-not (Test-Path $pythonScript)) {
    Write-Host "❌ Error: start_continuous_email_service.py not found!" -ForegroundColor Red
    exit 1
}

Write-Host "`n🔧 Creating Windows Scheduled Task..." -ForegroundColor Cyan

# Task details
$taskName = "ClassWave_Email_Service"
$taskDescription = "Automatic email service for ClassWave - sends daily digest emails at student preference times"

# Create the scheduled task action
$action = New-ScheduledTaskAction -Execute $pythonExe -Argument $pythonScript -WorkingDirectory $currentDir

# Create trigger for system startup
$trigger = New-ScheduledTaskTrigger -AtStartup

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

# Create principal (run as current user)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

try {
    # Register the scheduled task
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $taskDescription -Force
    
    Write-Host "✅ Scheduled task '$taskName' created successfully!" -ForegroundColor Green
    
    # Start the task immediately
    Start-ScheduledTask -TaskName $taskName
    Write-Host "✅ Email service started!" -ForegroundColor Green
    
    Write-Host "`n📋 TASK DETAILS:" -ForegroundColor Cyan
    Write-Host "   Name: $taskName"
    Write-Host "   Description: $taskDescription"
    Write-Host "   Trigger: At system startup"
    Write-Host "   Action: Run Python email service"
    Write-Host "   Auto-restart: Yes (if it stops)"
    
    Write-Host "`n🎯 WHAT HAPPENS NOW:" -ForegroundColor Green
    Write-Host "   ✅ Email service is running in background"
    Write-Host "   ✅ Will start automatically when computer boots"
    Write-Host "   ✅ Will restart automatically if it crashes"
    Write-Host "   ✅ Sends emails at exact preference times"
    
    Write-Host "`n📧 TODAY'S EMAIL SCHEDULE:" -ForegroundColor Yellow
    Write-Host "   • PranayaYadav: 4:10 PM"
    Write-Host "   • B.Anusha: 9:00 PM"
    Write-Host "   • A.Revathi: 11:55 PM"
    
    Write-Host "`n💡 MANAGEMENT COMMANDS:" -ForegroundColor Cyan
    Write-Host "   View task: Get-ScheduledTask -TaskName '$taskName'"
    Write-Host "   Stop task: Stop-ScheduledTask -TaskName '$taskName'"
    Write-Host "   Start task: Start-ScheduledTask -TaskName '$taskName'"
    Write-Host "   Remove task: Unregister-ScheduledTask -TaskName '$taskName'"
    
} catch {
    Write-Host "❌ Error creating scheduled task: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Try running PowerShell as Administrator" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n🎉 AUTOMATIC EMAIL SERVICE SETUP COMPLETE!" -ForegroundColor Green
Write-Host "The email service will now run automatically forever!" -ForegroundColor Green
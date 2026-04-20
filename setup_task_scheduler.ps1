
# ClassWave Daily Digest Task Scheduler Setup
$TaskName = "ClassWave Daily Digest"
$TaskDescription = "Automatically generate and send daily digest emails to students"
$BatchFile = "C:\Users\velma\OneDrive\Desktop\Lecturebuzz\daily_digest_automation.bat"
$TriggerTime = "06:00"

Write-Host "🤖 Setting up Windows Task Scheduler for ClassWave Daily Digest"
Write-Host "📅 Task Name: $TaskName"
Write-Host "⏰ Run Time: $TriggerTime daily"
Write-Host "📁 Batch File: $BatchFile"

try {
    # Delete existing task if it exists
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    
    # Create new scheduled task
    $Action = New-ScheduledTaskAction -Execute $BatchFile
    $Trigger = New-ScheduledTaskTrigger -Daily -At $TriggerTime
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description $TaskDescription
    
    Write-Host "✅ Task scheduled successfully!"
    Write-Host "📧 Daily digests will be sent automatically at $TriggerTime every day"
    Write-Host ""
    Write-Host "🔍 To verify the task:"
    Write-Host "   1. Open Task Scheduler (taskschd.msc)"
    Write-Host "   2. Look for '$TaskName' in Task Scheduler Library"
    Write-Host ""
    Write-Host "🧪 To test the task manually:"
    Write-Host "   schtasks /run /tn `"$TaskName`""
    
} catch {
    Write-Host "❌ Error setting up task: $_"
    Write-Host "💡 You may need to run PowerShell as Administrator"
}

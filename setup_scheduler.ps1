# ClassWave Automatic Scheduler Setup
$TaskName = "ClassWave Daily Digest"
$TaskPath = "C:\Users\velma\OneDrive\Desktop\Lecturebuzz\daily_digest_task.bat"

# Delete existing task if it exists
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Create new task
$Action = New-ScheduledTaskAction -Execute $TaskPath
$Trigger1 = New-ScheduledTaskTrigger -Daily -At "06:00AM"
$Trigger2 = New-ScheduledTaskTrigger -Daily -At "12:00PM" 
$Trigger3 = New-ScheduledTaskTrigger -Daily -At "06:00PM"

$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger @($Trigger1, $Trigger2, $Trigger3) -Settings $Settings -Description "ClassWave automatic daily digest generation and sending"

Write-Host "Scheduled task created successfully!"
Write-Host "Will run 3 times daily: 6 AM, 12 PM, 6 PM"
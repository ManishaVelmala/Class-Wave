#!/usr/bin/env python
"""
Setup fully automatic daily digest system
This will create a Windows Task Scheduler task to run daily
"""

import os
import subprocess
from datetime import datetime

def setup_automatic_system():
    print("🤖 SETTING UP FULLY AUTOMATIC DAILY DIGEST SYSTEM")
    print("=" * 60)
    
    # Get current directory
    current_dir = os.getcwd()
    python_path = "python"  # Assumes python is in PATH
    
    # Create the daily digest command
    digest_command = f'cd /d "{current_dir}" && {python_path} generate_todays_digest.py'
    
    print(f"📁 Project Directory: {current_dir}")
    print(f"🐍 Python Command: {python_path}")
    print(f"📧 Digest Command: {digest_command}")
    
    # Create batch file for Windows Task Scheduler
    batch_content = f"""@echo off
REM ClassWave Daily Digest Automation
REM This runs every day at 6:00 AM to generate and send daily digests

echo ClassWave Daily Digest Service Starting...
echo Date: %date%
echo Time: %time%

cd /d "{current_dir}"

echo Generating today's digests...
{python_path} generate_todays_digest.py

echo ✅ Daily digest service completed
echo.
"""
    
    batch_file = "daily_digest_automation.bat"
    
    with open(batch_file, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print(f"✅ Created batch file: {batch_file}")
    
    # Create PowerShell script to setup Windows Task Scheduler
    powershell_script = f"""
# ClassWave Daily Digest Task Scheduler Setup
$TaskName = "ClassWave Daily Digest"
$TaskDescription = "Automatically generate and send daily digest emails to students"
$BatchFile = "{os.path.join(current_dir, batch_file)}"
$TriggerTime = "06:00"

Write-Host "🤖 Setting up Windows Task Scheduler for ClassWave Daily Digest"
Write-Host "📅 Task Name: $TaskName"
Write-Host "⏰ Run Time: $TriggerTime daily"
Write-Host "📁 Batch File: $BatchFile"

try {{
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
    
}} catch {{
    Write-Host "❌ Error setting up task: $_"
    Write-Host "💡 You may need to run PowerShell as Administrator"
}}
"""
    
    ps_file = "setup_task_scheduler.ps1"
    with open(ps_file, 'w', encoding='utf-8') as f:
        f.write(powershell_script)
    
    print(f"✅ Created PowerShell script: {ps_file}")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. Run as Administrator: powershell -ExecutionPolicy Bypass -File {ps_file}")
    print(f"2. Or manually run: {batch_file}")
    print(f"3. Or use the background service: python automatic_digest_service.py")
    
    print(f"\n📊 AUTOMATIC OPTIONS:")
    print(f"✅ Option 1: Windows Task Scheduler (Recommended)")
    print(f"   - Runs daily at 6:00 AM automatically")
    print(f"   - Works even when computer restarts")
    print(f"   - Professional solution")
    
    print(f"\n✅ Option 2: Background Service")
    print(f"   - Run: python automatic_digest_service.py")
    print(f"   - Continuous monitoring and sending")
    print(f"   - Must keep terminal open")
    
    print(f"\n✅ Option 3: Manual Daily Run")
    print(f"   - Run: {batch_file}")
    print(f"   - Or: python generate_todays_digest.py")
    print(f"   - Manual but reliable")

if __name__ == "__main__":
    setup_automatic_system()
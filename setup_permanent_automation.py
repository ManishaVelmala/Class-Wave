#!/usr/bin/env python
"""
Set up permanent automation for ClassWave digest system
"""

import os
import subprocess
import sys

def setup_permanent_automation():
    print("🚀 SETTING UP PERMANENT AUTOMATION")
    print("=" * 60)
    
    print("📋 AUTOMATION OPTIONS:")
    print()
    
    print("1️⃣ BACKGROUND SERVICE (Recommended)")
    print("   ✅ Runs 24/7 automatically")
    print("   ✅ No manual intervention needed")
    print("   ✅ Sends emails at exact times")
    print("   🔧 Command: python start_full_automation.py")
    print()
    
    print("2️⃣ WINDOWS TASK SCHEDULER")
    print("   ✅ Runs automatically on schedule")
    print("   ✅ Survives computer restarts")
    print("   ✅ Built into Windows")
    print("   🔧 Setup: Automated below")
    print()
    
    print("3️⃣ STARTUP AUTOMATION")
    print("   ✅ Starts when computer boots")
    print("   ✅ Always running in background")
    print("   ✅ No daily setup needed")
    print("   🔧 Setup: Automated below")
    print()
    
    choice = input("Choose option (1, 2, or 3): ").strip()
    
    if choice == "1":
        setup_background_service()
    elif choice == "2":
        setup_windows_scheduler()
    elif choice == "3":
        setup_startup_automation()
    else:
        print("❌ Invalid choice")

def setup_background_service():
    print("\n🔧 SETTING UP BACKGROUND SERVICE")
    print("=" * 40)
    
    print("📝 Creating service script...")
    
    # Create a service script that runs continuously
    service_script = '''@echo off
title ClassWave Automatic Service
echo 🚀 Starting ClassWave Automatic Service...
echo ✅ Emails will be sent automatically
echo 🛑 Close this window to stop the service
echo.

:loop
python start_full_automation.py
echo ⚠️ Service stopped. Restarting in 10 seconds...
timeout /t 10 /nobreak >nul
goto loop
'''
    
    with open('classwave_service.bat', 'w') as f:
        f.write(service_script)
    
    print("✅ Created: classwave_service.bat")
    
    print("\n🎯 TO START THE SERVICE:")
    print("   1. Double-click: classwave_service.bat")
    print("   2. Keep the window open")
    print("   3. Emails will be sent automatically!")
    
    print("\n💡 TIPS:")
    print("   • Minimize the window (don't close it)")
    print("   • Service will restart automatically if it crashes")
    print("   • Close the window to stop the service")

def setup_windows_scheduler():
    print("\n🔧 SETTING UP WINDOWS TASK SCHEDULER")
    print("=" * 40)
    
    current_dir = os.getcwd()
    python_path = sys.executable
    
    # Create batch file for task scheduler
    task_script = f'''@echo off
cd /d "{current_dir}"
"{python_path}" manage.py refresh_todays_digests
"{python_path}" manage.py send_due_emails
'''
    
    with open('daily_digest_task.bat', 'w') as f:
        f.write(task_script)
    
    print("✅ Created: daily_digest_task.bat")
    
    # Create PowerShell script to set up the scheduled task
    ps_script = f'''
$TaskName = "ClassWave Daily Digest"
$TaskPath = "{current_dir}\\daily_digest_task.bat"

# Delete existing task if it exists
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Create new task
$Action = New-ScheduledTaskAction -Execute $TaskPath
$Trigger1 = New-ScheduledTaskTrigger -Daily -At "06:00AM"
$Trigger2 = New-ScheduledTaskTrigger -Daily -At "12:00PM"
$Trigger3 = New-ScheduledTaskTrigger -Daily -At "06:00PM"

$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger @($Trigger1, $Trigger2, $Trigger3) -Settings $Settings -Description "ClassWave automatic daily digest generation and sending"

Write-Host "✅ Scheduled task created successfully!"
Write-Host "📅 Will run 3 times daily: 6 AM, 12 PM, 6 PM"
'''
    
    with open('setup_scheduler.ps1', 'w') as f:
        f.write(ps_script)
    
    print("✅ Created: setup_scheduler.ps1")
    
    print("\n🎯 TO SETUP WINDOWS SCHEDULER:")
    print("   1. Right-click PowerShell → Run as Administrator")
    print("   2. Run: Set-ExecutionPolicy RemoteSigned")
    print("   3. Run: .\\setup_scheduler.ps1")
    print("   4. Task will run automatically 3 times daily!")

def setup_startup_automation():
    print("\n🔧 SETTING UP STARTUP AUTOMATION")
    print("=" * 40)
    
    current_dir = os.getcwd()
    
    # Create startup script
    startup_script = f'''@echo off
cd /d "{current_dir}"
start /min python start_full_automation.py
'''
    
    startup_file = "classwave_startup.bat"
    with open(startup_file, 'w') as f:
        f.write(startup_script)
    
    print("✅ Created: classwave_startup.bat")
    
    # Get startup folder path
    startup_folder = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    
    print(f"\n🎯 TO SETUP STARTUP AUTOMATION:")
    print(f"   1. Copy: {startup_file}")
    print(f"   2. Paste to: {startup_folder}")
    print(f"   3. ClassWave will start automatically when computer boots!")
    
    print(f"\n💡 OR run this command:")
    print(f'   copy "{os.path.abspath(startup_file)}" "{startup_folder}"')

if __name__ == "__main__":
    setup_permanent_automation()
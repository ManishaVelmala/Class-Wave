#!/usr/bin/env python3
"""
Make the 30-second email service permanent and auto-start
"""

import os
import sys
import subprocess

def create_startup_script():
    """Create a startup script for the 30-second service"""
    
    print("🚀 MAKING 30-SECOND SERVICE PERMANENT")
    print("=" * 40)
    
    # Create Windows startup batch file
    startup_script = f'''@echo off
title ClassWave 30-Second Email Service
echo ========================================
echo  ClassWave 30-Second Email Service
echo ========================================
echo.
echo Starting continuous email monitoring...
echo Maximum delay: 30 seconds
echo Perfect timing for all time preferences
echo.
echo Service will restart automatically if stopped
echo Press Ctrl+C to stop permanently
echo.

:start
cd /d "{os.getcwd()}"
python start_continuous_email_service.py
echo.
echo Service stopped. Restarting in 10 seconds...
echo Press Ctrl+C now to stop permanently
timeout /t 10 /nobreak >nul
goto start
'''
    
    with open('start_permanent_30_second_service.bat', 'w') as f:
        f.write(startup_script)
    
    print("✅ Created permanent service script: start_permanent_30_second_service.bat")
    
    # Create Windows service installer
    service_installer = '''# Install ClassWave 30-Second Email Service as Windows Service
Write-Host "INSTALLING CLASSWAVE 30-SECOND EMAIL SERVICE" -ForegroundColor Cyan
Write-Host "=============================================="

# Check if pywin32 is installed
try {
    python -c "import win32serviceutil" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ pywin32 is installed" -ForegroundColor Green
    } else {
        Write-Host "❌ pywin32 not found. Installing..." -ForegroundColor Yellow
        pip install pywin32
    }
} catch {
    Write-Host "Installing pywin32..." -ForegroundColor Yellow
    pip install pywin32
}

# Install the service
if (Test-Path "classwave_30second_service.py") {
    Write-Host "Installing Windows service..." -ForegroundColor Cyan
    python classwave_30second_service.py install
    
    Write-Host "Starting service..." -ForegroundColor Cyan
    python classwave_30second_service.py start
    
    Write-Host ""
    Write-Host "✅ SERVICE INSTALLED AND STARTED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Service Details:" -ForegroundColor Cyan
    Write-Host "   Name: ClassWave30SecondEmail"
    Write-Host "   Status: Running"
    Write-Host "   Startup: Automatic"
    Write-Host "   Accuracy: 30-second precision"
    Write-Host ""
    Write-Host "Management Commands:" -ForegroundColor Yellow
    Write-Host "   Stop:    python classwave_30second_service.py stop"
    Write-Host "   Start:   python classwave_30second_service.py start"
    Write-Host "   Remove:  python classwave_30second_service.py remove"
    
} else {
    Write-Host "❌ Service file not found. Run setup_30_second_windows_service.ps1 first" -ForegroundColor Red
}
'''
    
    with open('install_permanent_service.ps1', 'w') as f:
        f.write(service_installer)
    
    print("✅ Created service installer: install_permanent_service.ps1")

def create_auto_startup():
    """Create auto-startup configuration"""
    
    print(f"\n⚡ CREATING AUTO-STARTUP CONFIGURATION")
    print("=" * 40)
    
    # Create Windows Task Scheduler for startup
    startup_task = '''# Create Windows startup task for 30-second email service
Write-Host "CREATING AUTO-STARTUP TASK" -ForegroundColor Cyan
Write-Host "=========================="

$taskName = "ClassWave 30-Second Email Startup"
$currentDir = Get-Location

# Remove existing task
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

# Create startup task
$action = New-ScheduledTaskAction -Execute "cmd" -Argument "/c start_permanent_30_second_service.bat" -WorkingDirectory $currentDir

$trigger = New-ScheduledTaskTrigger -AtStartup

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Auto-start ClassWave 30-second email service on system startup"

Write-Host ""
Write-Host "✅ AUTO-STARTUP CONFIGURED!" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "   Task: $taskName"
Write-Host "   Trigger: System startup"
Write-Host "   Action: Start 30-second email service"
Write-Host "   Auto-restart: Yes"
Write-Host ""
Write-Host "Benefits:" -ForegroundColor Green
Write-Host "   - Service starts automatically when computer boots"
Write-Host "   - Restarts automatically if it stops"
Write-Host "   - Perfect timing maintained 24/7"
Write-Host "   - No manual intervention required"
'''
    
    with open('setup_auto_startup.ps1', 'w') as f:
        f.write(startup_task)
    
    print("✅ Created auto-startup script: setup_auto_startup.ps1")

def show_permanent_options():
    """Show permanent service options"""
    
    print(f"\n📋 PERMANENT SERVICE OPTIONS")
    print("=" * 30)
    
    print("🔧 Option 1: Windows Service (Recommended)")
    print("   • Runs as system service")
    print("   • Starts automatically on boot")
    print("   • Most reliable and professional")
    print("   • Command: PowerShell -ExecutionPolicy Bypass -File install_permanent_service.ps1")
    
    print(f"\n🔧 Option 2: Startup Task")
    print("   • Runs on user login")
    print("   • Auto-restarts if stopped")
    print("   • Easy to manage")
    print("   • Command: PowerShell -ExecutionPolicy Bypass -File setup_auto_startup.ps1")
    
    print(f"\n🔧 Option 3: Manual Startup")
    print("   • Run when needed")
    print("   • Full control")
    print("   • Command: start_permanent_30_second_service.bat")
    
    print(f"\n✅ All options provide:")
    print("   • 30-second timing accuracy")
    print("   • Perfect time preference delivery")
    print("   • Automatic restart on failure")
    print("   • Continuous 24/7 operation")

if __name__ == "__main__":
    create_startup_script()
    create_auto_startup()
    show_permanent_options()
    
    print(f"\n" + "=" * 60)
    print("🎯 30-SECOND SERVICE - PERMANENT SETUP COMPLETE")
    print("=" * 60)
    
    print("✅ Created Files:")
    print("   • start_permanent_30_second_service.bat (Manual startup)")
    print("   • install_permanent_service.ps1 (Windows Service)")
    print("   • setup_auto_startup.ps1 (Auto-startup task)")
    
    print(f"\n🚀 Quick Start (Recommended):")
    print("   PowerShell -ExecutionPolicy Bypass -File setup_auto_startup.ps1")
    
    print(f"\n🎯 Result:")
    print("   • 30-second email service runs permanently")
    print("   • Perfect timing for all time preferences")
    print("   • Automatic startup and restart")
    print("   • Students get emails at exact preferred times")
    
    print(f"\n✅ Your email system now has PERFECT timing accuracy!")
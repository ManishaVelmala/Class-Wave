#!/usr/bin/env python3
"""
Make the email system fully automatic
- Creates Windows startup entry
- Sets up monitoring
- Provides management tools
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_startup_entry():
    """Create Windows startup entry for the email service"""
    
    print("🔧 CREATING AUTOMATIC STARTUP")
    print("=" * 30)
    
    # Get paths
    current_dir = os.getcwd()
    startup_folder = os.path.join(os.environ['APPDATA'], 
                                 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    
    startup_script_path = os.path.join(startup_folder, 'ClassWave_Email_Service.bat')
    
    print(f"📍 Current directory: {current_dir}")
    print(f"📁 Startup folder: {startup_folder}")
    
    # Create startup batch file
    startup_content = f'''@echo off
cd /d "{current_dir}"
echo Starting ClassWave Email Service...
echo Service will run in background and send emails at correct times
echo.
echo Today's email schedule:
echo - PranayaYadav: 4:10 PM
echo - B.Anusha: 9:00 PM
echo - A.Revathi: 11:55 PM
echo.
python start_continuous_email_service.py
'''
    
    try:
        with open(startup_script_path, 'w') as f:
            f.write(startup_content)
        
        print(f"✅ Created startup script: {startup_script_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating startup script: {e}")
        return False

def create_management_tools():
    """Create management tools for the automatic service"""
    
    print(f"\n🛠️  CREATING MANAGEMENT TOOLS")
    print("=" * 30)
    
    # 1. Status checker
    status_script = '''@echo off
echo 📊 EMAIL SERVICE STATUS
echo =======================
echo.
python email_service_status.py
echo.
pause
'''
    
    with open('check_email_service.bat', 'w') as f:
        f.write(status_script)
    print("✅ Created: check_email_service.bat")
    
    # 2. Manual starter
    start_script = '''@echo off
echo 🚀 STARTING EMAIL SERVICE MANUALLY
echo ==================================
echo.
echo This will start the email service in this window
echo Keep this window open to keep the service running
echo.
echo Press Ctrl+C to stop the service
echo.
python start_continuous_email_service.py
'''
    
    with open('start_email_service_manual.bat', 'w') as f:
        f.write(start_script)
    print("✅ Created: start_email_service_manual.bat")
    
    # 3. Quick status check
    quick_check_script = '''#!/usr/bin/env python3
import os, sys, django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.utils import timezone
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

utc_now = timezone.now()
india_now = utc_now + timedelta(hours=5, minutes=30)
current_time = india_now.time()

print(f"⏰ Current India time: {current_time.strftime('%I:%M %p')}")

# Quick status
students = User.objects.filter(user_type='student')
sent_today = 0
pending_today = 0

for student in students:
    try:
        digest = Reminder.objects.filter(
            student=student,
            reminder_type='daily_digest',
            digest_date=india_now.date()
        ).first()
        
        if digest and digest.is_sent:
            sent_today += 1
        else:
            pending_today += 1
    except:
        pass

print(f"📧 Emails sent today: {sent_today}")
print(f"⏳ Emails pending: {pending_today}")

if pending_today > 0:
    print("💡 Make sure the email service is running!")
else:
    print("✅ All emails sent for today!")
'''
    
    with open('quick_status.py', 'w') as f:
        f.write(quick_check_script)
    print("✅ Created: quick_status.py")

def test_automatic_setup():
    """Test if the automatic setup is working"""
    
    print(f"\n🧪 TESTING AUTOMATIC SETUP")
    print("=" * 27)
    
    # Check if startup file exists
    startup_folder = os.path.join(os.environ['APPDATA'], 
                                 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    startup_file = os.path.join(startup_folder, 'ClassWave_Email_Service.bat')
    
    if os.path.exists(startup_file):
        print("✅ Startup script exists")
    else:
        print("❌ Startup script not found")
        return False
    
    # Check if email service script exists
    if os.path.exists('start_continuous_email_service.py'):
        print("✅ Email service script exists")
    else:
        print("❌ Email service script not found")
        return False
    
    # Check if management tools exist
    tools = ['check_email_service.bat', 'start_email_service_manual.bat', 'quick_status.py']
    for tool in tools:
        if os.path.exists(tool):
            print(f"✅ {tool} created")
        else:
            print(f"❌ {tool} not found")
    
    return True

def show_instructions():
    """Show instructions for using the automatic system"""
    
    print(f"\n📋 AUTOMATIC EMAIL SYSTEM INSTRUCTIONS")
    print("=" * 40)
    
    print(f"\n🎯 WHAT WAS SET UP:")
    print("   ✅ Windows startup entry - service starts when computer boots")
    print("   ✅ Management tools - easy status checking and control")
    print("   ✅ Monitoring scripts - track email delivery")
    
    print(f"\n🚀 HOW TO USE:")
    print("   1. AUTOMATIC (Recommended):")
    print("      • Restart your computer")
    print("      • Email service will start automatically")
    print("      • Runs in background forever")
    
    print(f"\n   2. MANUAL START (For now):")
    print("      • Double-click: start_email_service_manual.bat")
    print("      • Or run: python start_continuous_email_service.py")
    
    print(f"\n📊 MONITORING:")
    print("   • Double-click: check_email_service.bat")
    print("   • Or run: python email_service_status.py")
    print("   • Quick check: python quick_status.py")
    
    print(f"\n📧 TODAY'S SCHEDULE:")
    print("   • PranayaYadav: 4:10 PM")
    print("   • B.Anusha: 9:00 PM")
    print("   • A.Revathi: 11:55 PM")
    
    print(f"\n💡 IMPORTANT:")
    print("   • Service must be running to send emails")
    print("   • Check status regularly with monitoring tools")
    print("   • Emails sent within 30 seconds of preference time")

def main():
    """Main function to set up automatic email system"""
    
    print("🤖 MAKING EMAIL SYSTEM FULLY AUTOMATIC")
    print("=" * 40)
    
    print("This will set up the email service to run automatically!")
    
    # Step 1: Create startup entry
    startup_success = create_startup_entry()
    
    # Step 2: Create management tools
    create_management_tools()
    
    # Step 3: Test setup
    test_success = test_automatic_setup()
    
    # Step 4: Show instructions
    show_instructions()
    
    if startup_success and test_success:
        print(f"\n🎉 AUTOMATIC EMAIL SYSTEM SETUP COMPLETE!")
        print("=" * 42)
        print("✅ Email service will now start automatically when Windows boots")
        print("✅ Emails will be sent at exact preference times")
        print("✅ System runs in background continuously")
        
        print(f"\n🚀 TO START NOW (without reboot):")
        print("   Double-click: start_email_service_manual.bat")
        
    else:
        print(f"\n⚠️  SETUP COMPLETED WITH SOME ISSUES")
        print("Check the errors above and try running as Administrator")

if __name__ == "__main__":
    main()
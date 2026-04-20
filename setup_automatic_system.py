#!/usr/bin/env python3
"""
Set up automatic email system without Unicode issues
"""

import os
import sys

def create_startup_entry():
    """Create Windows startup entry for the email service"""
    
    print("CREATING AUTOMATIC STARTUP")
    print("=" * 30)
    
    # Get paths
    current_dir = os.getcwd()
    startup_folder = os.path.join(os.environ['APPDATA'], 
                                 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    
    startup_script_path = os.path.join(startup_folder, 'ClassWave_Email_Service.bat')
    
    print(f"Current directory: {current_dir}")
    print(f"Startup folder: {startup_folder}")
    
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
        
        print(f"SUCCESS: Created startup script: {startup_script_path}")
        return True
        
    except Exception as e:
        print(f"ERROR: Could not create startup script: {e}")
        return False

def create_management_tools():
    """Create management tools for the automatic service"""
    
    print(f"\nCREATING MANAGEMENT TOOLS")
    print("=" * 30)
    
    # 1. Status checker
    status_script = '''@echo off
echo EMAIL SERVICE STATUS
echo ====================
echo.
python email_service_status.py
echo.
pause
'''
    
    with open('check_email_service.bat', 'w') as f:
        f.write(status_script)
    print("SUCCESS: Created check_email_service.bat")
    
    # 2. Manual starter
    start_script = '''@echo off
echo STARTING EMAIL SERVICE MANUALLY
echo ================================
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
    print("SUCCESS: Created start_email_service_manual.bat")

def show_final_instructions():
    """Show final instructions"""
    
    print(f"\nAUTOMATIC EMAIL SYSTEM SETUP COMPLETE!")
    print("=" * 40)
    
    print(f"\nWHAT WAS SET UP:")
    print("   - Windows startup entry created")
    print("   - Management tools created")
    print("   - Email service will start automatically on boot")
    
    print(f"\nHOW TO USE:")
    print("   1. AUTOMATIC (Recommended):")
    print("      - Restart your computer")
    print("      - Email service starts automatically")
    print("      - Runs in background forever")
    
    print(f"\n   2. START NOW (Manual):")
    print("      - Double-click: start_email_service_manual.bat")
    print("      - Or run: python start_continuous_email_service.py")
    
    print(f"\nMONITORING:")
    print("   - Double-click: check_email_service.bat")
    print("   - Or run: python email_service_status.py")
    
    print(f"\nTODAY'S REMAINING EMAILS:")
    print("   - PranayaYadav: 4:10 PM")
    print("   - B.Anusha: 9:00 PM")
    print("   - A.Revathi: 11:55 PM")
    
    print(f"\nIMPORTANT:")
    print("   - Service must be running to send emails")
    print("   - Emails sent within 30 seconds of preference time")
    print("   - Check status regularly")

def main():
    """Main function"""
    
    print("MAKING EMAIL SYSTEM FULLY AUTOMATIC")
    print("=" * 36)
    
    # Create startup entry
    startup_success = create_startup_entry()
    
    # Create management tools
    create_management_tools()
    
    # Show instructions
    show_final_instructions()
    
    if startup_success:
        print(f"\nSUCCESS: Email system is now fully automatic!")
        print("Restart your computer or run manually to start sending emails.")
    else:
        print(f"\nWARNING: Some issues occurred. Try running as Administrator.")

if __name__ == "__main__":
    main()
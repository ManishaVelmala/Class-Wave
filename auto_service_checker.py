#!/usr/bin/env python3
"""
Automatic Service Checker - Lightweight background monitor
Checks every 2 minutes if email service is running
Automatically restarts if needed
"""

import os
import sys
import django
import time
import subprocess
import psutil
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

def is_email_service_running():
    """Check if email service is running"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] in ['python.exe', 'python']:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'start_continuous_email_service.py' in cmdline:
                    return True, proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False, None

def start_email_service():
    """Start the email service"""
    try:
        subprocess.Popen(
            [sys.executable, 'start_continuous_email_service.py'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=os.getcwd()
        )
        time.sleep(3)  # Wait for startup
        return is_email_service_running()[0]
    except:
        return False

def main():
    """Main monitoring loop"""
    
    print("🔍 AUTO SERVICE CHECKER STARTED")
    print("=" * 32)
    print("Checking email service every 2 minutes")
    print("Press Ctrl+C to stop")
    
    restart_count = 0
    max_restarts = 5
    
    try:
        while True:
            running, pid = is_email_service_running()
            current_time = datetime.now().strftime('%H:%M:%S')
            
            if running:
                print(f"✅ {current_time} - Email service running (PID: {pid})")
            else:
                print(f"🚨 {current_time} - Email service NOT running!")
                
                if restart_count < max_restarts:
                    print(f"🔄 Attempting restart #{restart_count + 1}...")
                    if start_email_service():
                        restart_count += 1
                        print(f"✅ Service restarted successfully")
                    else:
                        print(f"❌ Failed to restart service")
                else:
                    print(f"❌ Max restarts reached. Manual intervention needed.")
            
            time.sleep(120)  # Check every 2 minutes
            
    except KeyboardInterrupt:
        print(f"\n🛑 Auto checker stopped")

if __name__ == "__main__":
    main()
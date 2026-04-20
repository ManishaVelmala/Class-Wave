#!/usr/bin/env python3
"""
Auto Start Email Service - Automatically starts the email service when opening the project
This should be run every time you open the project folder in VSCode/Kiro
"""

import os
import sys
import django
import subprocess
import time
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.utils import timezone
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def check_if_service_running():
    """Check if the email service is already running"""
    
    try:
        # Check for Python processes running the email service
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        
        # Look for our specific service (this is a simple check)
        if 'python.exe' in result.stdout:
            print("🔍 Found Python processes running")
            return True
        else:
            print("❌ No Python processes found")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not check processes: {e}")
        return False

def check_service_health():
    """Check if the email service is working properly"""
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    current_time = india_now.time()
    
    # Check for overdue emails (indicates service not working)
    students = User.objects.filter(user_type='student')
    overdue_count = 0
    
    for student in students:
        try:
            pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=india_date
            ).first()
            
            if digest and not digest.is_sent:
                # Check if email is overdue (more than 5 minutes past preference time)
                pref_datetime = datetime.combine(india_date, pref.digest_time)
                current_datetime = datetime.combine(india_date, current_time)
                
                if current_datetime > pref_datetime:
                    time_overdue = current_datetime - pref_datetime
                    if time_overdue.total_seconds() > 300:  # More than 5 minutes
                        overdue_count += 1
                        
        except DailyDigestPreference.DoesNotExist:
            continue
    
    return overdue_count == 0

def start_email_service():
    """Start the email service in the background"""
    
    print("🚀 STARTING EMAIL SERVICE...")
    
    try:
        # Start the service as a detached process
        if os.name == 'nt':  # Windows
            # Use CREATE_NEW_PROCESS_GROUP to detach from current process
            subprocess.Popen(
                [sys.executable, 'start_continuous_email_service.py'],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=os.getcwd()
            )
        else:  # Linux/Mac
            subprocess.Popen(
                [sys.executable, 'start_continuous_email_service.py'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=os.getcwd()
            )
        
        print("✅ Email service started successfully!")
        print("   Service will run in background and check every 30 seconds")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start email service: {e}")
        return False

def show_project_status():
    """Show the current project and email status"""
    
    print("📊 PROJECT EMAIL SERVICE STATUS")
    print("=" * 33)
    
    current_time = datetime.now()
    print(f"Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project: {os.path.basename(os.getcwd())}")
    
    # Check email statistics
    try:
        utc_now = timezone.now()
        india_now = utc_now + timedelta(hours=5, minutes=30)
        india_date = india_now.date()
        
        students = User.objects.filter(user_type='student')
        sent_today = 0
        pending_today = 0
        
        for student in students:
            try:
                digest = Reminder.objects.filter(
                    student=student,
                    reminder_type='daily_digest',
                    digest_date=india_date
                ).first()
                
                if digest and digest.is_sent:
                    sent_today += 1
                else:
                    pending_today += 1
                    
            except:
                continue
        
        print(f"\n📧 Today's Email Status:")
        print(f"   ✅ Sent: {sent_today}")
        print(f"   ⏳ Pending: {pending_today}")
        
        if pending_today > 0:
            print(f"   💡 Background service needed to send pending emails")
        else:
            print(f"   🎉 All emails sent for today!")
            
    except Exception as e:
        print(f"⚠️  Could not check email status: {e}")

def main():
    """Main function - Auto start email service when project opens"""
    
    print("🔄 AUTO-START EMAIL SERVICE")
    print("=" * 28)
    print("Checking if email service needs to be started...")
    
    # Show current project status
    show_project_status()
    
    # Check if service is already running
    print(f"\n🔍 CHECKING SERVICE STATUS...")
    
    service_running = check_if_service_running()
    service_healthy = check_service_health()
    
    if service_running and service_healthy:
        print("✅ Email service is already running and healthy!")
        print("   No action needed - emails will be sent automatically")
        
    elif service_running and not service_healthy:
        print("⚠️  Email service is running but may have issues")
        print("   Consider restarting the service")
        
        restart = input("Restart email service? (y/n): ").lower().strip()
        if restart == 'y':
            print("🔄 Restarting email service...")
            start_email_service()
        
    else:
        print("❌ Email service is NOT running")
        print("   Starting email service automatically...")
        
        if start_email_service():
            # Wait a moment and verify it started
            time.sleep(3)
            print("✅ Email service should now be running!")
        else:
            print("❌ Failed to start email service")
            print("💡 Try running manually: python start_continuous_email_service.py")
    
    print(f"\n💡 QUICK COMMANDS:")
    print(f"   Check status: python email_service_status.py")
    print(f"   Manual start: python start_continuous_email_service.py")
    print(f"   Live monitor: python email_service_dashboard.py")
    
    print(f"\n🎯 REMEMBER:")
    print(f"   • Run this script every time you open the project")
    print(f"   • Email service stops when you close Kiro/VSCode")
    print(f"   • Service sends emails automatically at preference times")

if __name__ == "__main__":
    main()
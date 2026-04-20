#!/usr/bin/env python3
"""
Service Health Monitor - Ensures email service is always running
Automatically restarts the service if it stops
Monitors email delivery and timing accuracy
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

from django.utils import timezone
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

class EmailServiceMonitor:
    def __init__(self):
        self.service_process = None
        self.last_health_check = None
        self.restart_count = 0
        self.max_restarts = 10
        
    def is_email_service_running(self):
        """Check if the email service process is running"""
        
        # Check for Python processes running the email service
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'start_continuous_email_service.py' in cmdline:
                        self.service_process = proc
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return False
    
    def start_email_service(self):
        """Start the email service"""
        
        print(f"🚀 STARTING EMAIL SERVICE")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Start the service as a subprocess
            process = subprocess.Popen(
                [sys.executable, 'start_continuous_email_service.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Give it a moment to start
            time.sleep(3)
            
            if self.is_email_service_running():
                print("✅ Email service started successfully")
                self.restart_count += 1
                return True
            else:
                print("❌ Failed to start email service")
                return False
                
        except Exception as e:
            print(f"❌ Error starting email service: {e}")
            return False
    
    def check_email_timing_accuracy(self):
        """Check if emails are being sent at correct times"""
        
        utc_now = timezone.now()
        india_now = utc_now + timedelta(hours=5, minutes=30)
        india_date = india_now.date()
        
        timing_issues = []
        
        students = User.objects.filter(user_type='student')
        
        for student in students:
            try:
                pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
                digest = Reminder.objects.filter(
                    student=student,
                    reminder_type='daily_digest',
                    digest_date=india_date,
                    is_sent=True
                ).first()
                
                if digest and digest.sent_at:
                    sent_time = (digest.sent_at + timedelta(hours=5, minutes=30)).time()
                    pref_time = pref.digest_time
                    
                    # Check if sent too early (more than 2 hours)
                    if sent_time < pref_time:
                        time_diff = datetime.combine(india_date, pref_time) - datetime.combine(india_date, sent_time)
                        hours_early = time_diff.total_seconds() / 3600
                        
                        if hours_early > 2:
                            timing_issues.append({
                                'student': student.username,
                                'preference': pref_time,
                                'sent': sent_time,
                                'hours_early': hours_early
                            })
                            
            except DailyDigestPreference.DoesNotExist:
                continue
        
        return timing_issues
    
    def get_service_status(self):
        """Get comprehensive service status"""
        
        utc_now = timezone.now()
        india_now = utc_now + timedelta(hours=5, minutes=30)
        india_date = india_now.date()
        current_time = india_now.time()
        
        status = {
            'service_running': self.is_email_service_running(),
            'current_time': current_time,
            'current_date': india_date,
            'emails_sent_today': 0,
            'emails_pending': 0,
            'next_email': None,
            'timing_issues': self.check_email_timing_accuracy()
        }
        
        students = User.objects.filter(user_type='student')
        upcoming_emails = []
        
        for student in students:
            try:
                pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
                digest = Reminder.objects.filter(
                    student=student,
                    reminder_type='daily_digest',
                    digest_date=india_date
                ).first()
                
                if digest and digest.is_sent:
                    status['emails_sent_today'] += 1
                else:
                    status['emails_pending'] += 1
                    
                    # Calculate time until email
                    pref_datetime = datetime.combine(india_date, pref.digest_time)
                    current_datetime = datetime.combine(india_date, current_time)
                    
                    if pref_datetime > current_datetime:
                        time_until = pref_datetime - current_datetime
                        hours_until = time_until.total_seconds() / 3600
                        
                        upcoming_emails.append({
                            'student': student.username,
                            'time': pref.digest_time,
                            'hours_until': hours_until
                        })
                        
            except DailyDigestPreference.DoesNotExist:
                continue
        
        # Find next email
        if upcoming_emails:
            upcoming_emails.sort(key=lambda x: x['hours_until'])
            status['next_email'] = upcoming_emails[0]
        
        return status
    
    def print_status_report(self, status):
        """Print detailed status report"""
        
        print(f"\n📊 EMAIL SERVICE HEALTH REPORT")
        print(f"=" * 35)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"India Time: {status['current_time'].strftime('%I:%M %p')}")
        
        # Service status
        if status['service_running']:
            print(f"🟢 Email Service: RUNNING")
        else:
            print(f"🔴 Email Service: STOPPED")
        
        # Email statistics
        print(f"\n📧 EMAIL STATISTICS:")
        print(f"   Sent today: {status['emails_sent_today']}")
        print(f"   Pending: {status['emails_pending']}")
        
        # Next email
        if status['next_email']:
            next_email = status['next_email']
            if next_email['hours_until'] < 1:
                minutes = next_email['hours_until'] * 60
                print(f"   Next email: {next_email['student']} in {minutes:.0f} minutes")
            else:
                print(f"   Next email: {next_email['student']} in {next_email['hours_until']:.1f} hours")
        else:
            print(f"   Next email: All sent for today")
        
        # Timing issues
        if status['timing_issues']:
            print(f"\n⚠️  TIMING ISSUES DETECTED:")
            for issue in status['timing_issues']:
                print(f"   🚨 {issue['student']}: {issue['hours_early']:.1f}h early")
        else:
            print(f"\n✅ NO TIMING ISSUES")
        
        print(f"   Restart count: {self.restart_count}")
    
    def run_health_check(self):
        """Run a complete health check"""
        
        status = self.get_service_status()
        self.print_status_report(status)
        
        # Check if service needs to be restarted
        if not status['service_running']:
            print(f"\n🚨 EMAIL SERVICE NOT RUNNING!")
            
            if self.restart_count < self.max_restarts:
                print(f"🔄 Attempting to restart service...")
                if self.start_email_service():
                    print(f"✅ Service restarted successfully")
                else:
                    print(f"❌ Failed to restart service")
            else:
                print(f"❌ Max restart attempts reached ({self.max_restarts})")
                print(f"💡 Manual intervention required")
        
        self.last_health_check = datetime.now()
        return status
    
    def monitor_continuously(self, check_interval=300):  # 5 minutes
        """Monitor the service continuously"""
        
        print(f"🔍 STARTING CONTINUOUS EMAIL SERVICE MONITORING")
        print(f"=" * 48)
        print(f"Check interval: {check_interval} seconds ({check_interval//60} minutes)")
        print(f"Max restarts: {self.max_restarts}")
        print(f"Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                self.run_health_check()
                
                print(f"\n⏰ Next check in {check_interval//60} minutes...")
                print(f"=" * 50)
                
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")

def main():
    """Main function"""
    
    print(f"🔍 EMAIL SERVICE HEALTH MONITOR")
    print(f"=" * 32)
    
    monitor = EmailServiceMonitor()
    
    # Run initial health check
    status = monitor.run_health_check()
    
    print(f"\n💡 MONITORING OPTIONS:")
    print(f"1. Run continuous monitoring (recommended)")
    print(f"2. Single health check only")
    
    choice = input(f"\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        print(f"\n🔄 Starting continuous monitoring...")
        monitor.monitor_continuously()
    else:
        print(f"\n✅ Single health check complete")
        
        if not status['service_running']:
            print(f"\n⚠️  WARNING: Email service is not running!")
            print(f"💡 Start it manually with: python start_continuous_email_service.py")

if __name__ == "__main__":
    main()
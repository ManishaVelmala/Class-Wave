#!/usr/bin/env python3
"""
Continuous monitoring system for ALL students email timing
Prevents issues like Vaishnavi's case from happening to any student
"""

import os
import sys
import django
import time
from datetime import date, time as time_class, datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

class AllStudentsEmailMonitor:
    """Continuous monitoring system for all students"""
    
    def __init__(self):
        self.running = False
        self.last_check_minute = None
        self.total_fixes_applied = 0
        
    def start(self):
        """Start continuous monitoring"""
        
        print("🔍 STARTING ALL STUDENTS EMAIL MONITOR")
        print("=" * 40)
        print("⏰ Monitoring ALL students every 30 seconds")
        print("🔧 Auto-fixes overdue emails immediately")
        print("📊 Prevents issues like Vaishnavi's case")
        print("🎯 Ensures perfect email timing for everyone")
        print("")
        
        self.running = True
        
        try:
            while self.running:
                current_time = timezone.now()
                current_minute = current_time.replace(second=0, microsecond=0)
                
                # Check once per minute to avoid spam
                if self.last_check_minute != current_minute:
                    self.monitor_all_students()
                    self.last_check_minute = current_minute
                
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            print(f"\n🛑 Stopping all students monitor...")
            print(f"📊 Total fixes applied during session: {self.total_fixes_applied}")
            self.running = False
    
    def monitor_all_students(self):
        """Monitor all students and fix issues"""
        
        utc_now = timezone.now()
        india_now = utc_now + timedelta(hours=5, minutes=30)
        current_india_time = india_now.time()
        india_date = india_now.date()
        
        students = User.objects.filter(user_type='student')
        
        issues_found = 0
        fixes_applied = 0
        
        for student in students:
            try:
                # Check preference
                pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
                student_time = pref.digest_time
                
                # Check if email should be sent
                is_due = current_india_time >= student_time
                
                if is_due:
                    # Check digest status
                    digest = Reminder.objects.filter(
                        student=student,
                        reminder_type='daily_digest',
                        digest_date=india_date,
                        is_sent=False
                    ).first()
                    
                    if digest:
                        # Email is overdue - fix it!
                        time_overdue = datetime.combine(date.today(), current_india_time) - datetime.combine(date.today(), student_time)
                        minutes_overdue = int(time_overdue.total_seconds() // 60)
                        
                        if minutes_overdue >= 2:  # Only fix if 2+ minutes overdue
                            print(f"🚨 OVERDUE: {student.username} ({minutes_overdue}m overdue)")
                            
                            success = self.send_overdue_email(student, digest, india_date, student_time)
                            
                            if success:
                                fixes_applied += 1
                                self.total_fixes_applied += 1
                                print(f"   ✅ AUTO-FIXED: Email sent successfully!")
                            else:
                                print(f"   ❌ AUTO-FIX FAILED")
                            
                            issues_found += 1
                
            except DailyDigestPreference.DoesNotExist:
                # Student has no preference - create default
                print(f"⚠️  {student.username}: No preference - creating default (7:00 AM)")
                
                DailyDigestPreference.objects.create(
                    student=student,
                    digest_time=time_class(7, 0),
                    is_enabled=True
                )
                
                fixes_applied += 1
                self.total_fixes_applied += 1
                issues_found += 1
        
        # Only print summary if issues were found
        if issues_found > 0:
            print(f"📊 Monitor cycle: {issues_found} issues found, {fixes_applied} fixed")
    
    def send_overdue_email(self, student, digest, target_date, student_time):
        """Send overdue email with retry"""
        
        try:
            send_mail(
                subject=f'📅 Your Schedule for {target_date.strftime("%A, %B %d")}',
                message=digest.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=False,
            )
            
            # Mark as sent
            digest.is_sent = True
            digest.sent_at = timezone.now()
            digest.save()
            
            return True
            
        except Exception as e:
            print(f"   Error: {str(e)[:50]}...")
            return False

def create_daily_summary_report():
    """Create daily summary report for all students"""
    
    print("📊 DAILY SUMMARY REPORT - ALL STUDENTS")
    print("=" * 40)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    current_india_time = india_now.time()
    
    print(f"Report Date: {india_date}")
    print(f"India Time: {current_india_time.strftime('%I:%M %p')}")
    
    students = User.objects.filter(user_type='student')
    
    print(f"\n👥 ALL STUDENTS STATUS:")
    
    total_sent = 0
    total_pending = 0
    total_overdue = 0
    total_no_preference = 0
    
    for student in students:
        try:
            pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
            student_time = pref.digest_time
            
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=india_date
            ).first()
            
            if digest and digest.is_sent:
                india_sent_time = digest.sent_at + timedelta(hours=5, minutes=30)
                print(f"✅ {student.username}: Sent at {india_sent_time.strftime('%I:%M %p')} (due: {student_time.strftime('%I:%M %p')})")
                total_sent += 1
                
            elif current_india_time >= student_time:
                if digest:
                    time_overdue = datetime.combine(date.today(), current_india_time) - datetime.combine(date.today(), student_time)
                    minutes_overdue = int(time_overdue.total_seconds() // 60)
                    print(f"🚨 {student.username}: OVERDUE by {minutes_overdue}m (due: {student_time.strftime('%I:%M %p')})")
                    total_overdue += 1
                else:
                    print(f"❌ {student.username}: DUE but no digest (due: {student_time.strftime('%I:%M %p')})")
                    total_overdue += 1
            else:
                time_until = datetime.combine(date.today(), student_time) - datetime.combine(date.today(), current_india_time)
                hours = int(time_until.total_seconds() // 3600)
                minutes = int((time_until.total_seconds() % 3600) // 60)
                print(f"⏳ {student.username}: Due in {hours}h {minutes}m (at {student_time.strftime('%I:%M %p')})")
                total_pending += 1
                
        except DailyDigestPreference.DoesNotExist:
            print(f"⚠️  {student.username}: No time preference set")
            total_no_preference += 1
    
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Emails sent: {total_sent}")
    print(f"   ⏳ Pending: {total_pending}")
    print(f"   🚨 Overdue: {total_overdue}")
    print(f"   ⚠️  No preference: {total_no_preference}")
    
    # Health assessment
    if total_overdue == 0 and total_no_preference == 0:
        health = "✅ EXCELLENT"
    elif total_overdue <= 1:
        health = "⚠️  GOOD"
    else:
        health = "🚨 NEEDS ATTENTION"
    
    print(f"\n🏥 SYSTEM HEALTH: {health}")
    
    return total_overdue == 0 and total_no_preference == 0

def show_monitoring_options():
    """Show monitoring options"""
    
    print("🔧 ALL STUDENTS MONITORING OPTIONS")
    print("=" * 36)
    
    print("1. CONTINUOUS MONITORING:")
    print("   python continuous_all_students_monitor.py")
    print("   • Monitors all students every 30 seconds")
    print("   • Auto-fixes overdue emails immediately")
    print("   • Prevents issues like Vaishnavi's case")
    
    print(f"\n2. DAILY SUMMARY:")
    print("   python -c \"from continuous_all_students_monitor import create_daily_summary_report; create_daily_summary_report()\"")
    print("   • Shows status of all students")
    print("   • Identifies any issues")
    
    print(f"\n3. ONE-TIME CHECK & FIX:")
    print("   python verify_and_fix_all_students_email_timing.py")
    print("   • Comprehensive check of all students")
    print("   • Fixes all found issues")
    
    print(f"\n4. INDIVIDUAL STUDENT:")
    print("   python monitor_student_email.py <username>")
    print("   • Check specific student")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "summary":
        create_daily_summary_report()
    elif len(sys.argv) > 1 and sys.argv[1] == "options":
        show_monitoring_options()
    else:
        print("🔍 Starting continuous monitoring for ALL students...")
        print("This will prevent email timing issues for everyone!")
        print("Press Ctrl+C to stop")
        print("")
        
        monitor = AllStudentsEmailMonitor()
        monitor.start()
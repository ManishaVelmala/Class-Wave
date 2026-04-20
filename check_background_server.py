#!/usr/bin/env python3
"""
Check Background Server - Comprehensive check if email service is running
Uses multiple methods to verify service status
"""

import os
import sys
import django
import subprocess
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.utils import timezone
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def check_system_processes():
    """Check system processes for email service"""
    
    print("🔍 CHECKING SYSTEM PROCESSES")
    print("=" * 30)
    
    try:
        # Windows tasklist command
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        
        python_processes = []
        lines = result.stdout.split('\n')
        
        for line in lines:
            if 'python.exe' in line and line.strip():
                python_processes.append(line.strip())
        
        print(f"Found {len(python_processes)} Python processes:")
        for i, process in enumerate(python_processes, 1):
            print(f"   {i}. {process}")
        
        if python_processes:
            print("✅ Python processes detected (email service likely running)")
            return True
        else:
            print("❌ No Python processes found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking processes: {e}")
        return False

def check_service_functionality():
    """Check if service is functioning by looking at email delivery"""
    
    print(f"\n📧 CHECKING SERVICE FUNCTIONALITY")
    print("=" * 34)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    current_time = india_now.time()
    
    print(f"Current India time: {current_time.strftime('%I:%M %p')}")
    
    # Check for overdue emails
    students = User.objects.filter(user_type='student')
    overdue_emails = []
    sent_today = 0
    pending_today = 0
    
    for student in students:
        try:
            pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
            digest = Reminder.objects.filter(
                student=student,
                reminder_type='daily_digest',
                digest_date=india_date
            ).first()
            
            if digest and digest.is_sent:
                sent_today += 1
            else:
                pending_today += 1
                
                # Check if email is overdue (more than 5 minutes past preference)
                pref_datetime = datetime.combine(india_date, pref.digest_time)
                current_datetime = datetime.combine(india_date, current_time)
                
                if current_datetime > pref_datetime:
                    time_overdue = current_datetime - pref_datetime
                    if time_overdue.total_seconds() > 300:  # More than 5 minutes
                        overdue_emails.append({
                            'student': student.username,
                            'preference': pref.digest_time,
                            'overdue_minutes': time_overdue.total_seconds() / 60
                        })
                        
        except DailyDigestPreference.DoesNotExist:
            continue
    
    print(f"📊 Email Statistics:")
    print(f"   ✅ Sent today: {sent_today}")
    print(f"   ⏳ Pending: {pending_today}")
    print(f"   🚨 Overdue: {len(overdue_emails)}")
    
    if overdue_emails:
        print(f"\n⚠️  OVERDUE EMAILS DETECTED:")
        for email in overdue_emails:
            print(f"   🚨 {email['student']}: {email['overdue_minutes']:.0f} min overdue")
        print(f"   💡 This indicates service is NOT working properly")
        return False
    else:
        print(f"✅ No overdue emails - service appears functional")
        return True

def check_recent_activity():
    """Check for recent email service activity"""
    
    print(f"\n📈 CHECKING RECENT ACTIVITY")
    print("=" * 28)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    india_date = india_now.date()
    
    # Check for emails sent in last 4 hours
    four_hours_ago = utc_now - timedelta(hours=4)
    
    recent_emails = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=india_date,
        is_sent=True,
        sent_at__gte=four_hours_ago
    ).count()
    
    print(f"Emails sent in last 4 hours: {recent_emails}")
    
    if recent_emails > 0:
        print("✅ Recent email activity detected")
        return True
    else:
        print("⚠️  No recent email activity")
        return False

def comprehensive_server_check():
    """Run comprehensive background server check"""
    
    print("🔍 COMPREHENSIVE BACKGROUND SERVER CHECK")
    print("=" * 42)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all checks
    checks = {
        'system_processes': check_system_processes(),
        'service_functionality': check_service_functionality(),
        'recent_activity': check_recent_activity()
    }
    
    # Summary
    print(f"\n📊 CHECK RESULTS SUMMARY")
    print("=" * 26)
    
    passed_checks = sum(checks.values())
    total_checks = len(checks)
    
    for check_name, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        display_name = check_name.replace('_', ' ').title()
        print(f"   {display_name}: {status}")
    
    print(f"\n🎯 OVERALL ASSESSMENT:")
    
    if passed_checks == total_checks:
        print("✅ BACKGROUND SERVER IS RUNNING CORRECTLY")
        print("   • All checks passed")
        print("   • Service is active and functional")
        print("   • Emails will be sent at correct times")
        
    elif passed_checks >= 2:
        print("⚠️  BACKGROUND SERVER IS MOSTLY WORKING")
        print("   • Most checks passed")
        print("   • Service appears to be running")
        print("   • Monitor for any issues")
        
    else:
        print("🚨 BACKGROUND SERVER IS NOT WORKING")
        print("   • Multiple checks failed")
        print("   • Service may not be running")
        print("   • Immediate action needed")
    
    print(f"\n💡 QUICK ACTIONS:")
    if passed_checks < total_checks:
        print("   🚀 Start service: python auto_start_email_service.py")
        print("   🔄 Manual start: python start_continuous_email_service.py")
    
    print("   📊 Check status: python email_service_status.py")
    print("   🏥 Health check: python simple_service_monitor.py")
    
    return passed_checks, total_checks

def main():
    """Main function"""
    
    passed, total = comprehensive_server_check()
    
    print(f"\n📋 SUMMARY:")
    print(f"Background server check: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 Background server is running perfectly!")
    elif passed >= 2:
        print("⚠️  Background server has minor issues")
    else:
        print("🚨 Background server needs attention!")

if __name__ == "__main__":
    main()
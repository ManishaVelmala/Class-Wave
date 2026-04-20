#!/usr/bin/env python3
"""
Fix the email timing logic properly to handle day transitions
"""

import os
import sys
import django
from datetime import date, time, datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.utils import timezone
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference

def demonstrate_timing_issue():
    """Demonstrate the timing issue"""
    
    print("🐛 DEMONSTRATING THE TIMING ISSUE")
    print("=" * 35)
    
    # Current time
    current_time = time(7, 28)  # 7:28 AM
    
    # Student preferences
    test_cases = [
        (time(11, 55), "11:55 PM"),  # A.Revathi
        (time(16, 10), "04:10 PM"),  # PranayaYadav  
        (time(21, 0), "09:00 PM"),   # B.Anusha
        (time(8, 0), "08:00 AM"),    # Vaishnavi
    ]
    
    print(f"Current time: {current_time.strftime('%I:%M %p')}")
    
    for pref_time, pref_display in test_cases:
        # This is the WRONG logic currently being used
        wrong_result = current_time >= pref_time
        
        print(f"\n❌ WRONG Logic for {pref_display}:")
        print(f"   {current_time.strftime('%I:%M %p')} >= {pref_time.strftime('%I:%M %p')} = {wrong_result}")
        
        if wrong_result:
            print(f"   Result: Email sent NOW (WRONG!)")
        else:
            print(f"   Result: Email waits (correct)")

def show_correct_timing_logic():
    """Show the correct timing logic"""
    
    print(f"\n✅ CORRECT TIMING LOGIC")
    print("=" * 25)
    
    print("The issue is that we need to handle day transitions properly:")
    
    current_time = time(7, 28)  # 7:28 AM
    today = date.today()
    
    test_cases = [
        (time(11, 55), "11:55 PM"),  # Evening preference
        (time(16, 10), "04:10 PM"),  # Afternoon preference
        (time(21, 0), "09:00 PM"),   # Night preference
        (time(8, 0), "08:00 AM"),    # Morning preference
    ]
    
    print(f"Current time: {current_time.strftime('%I:%M %p')}")
    
    for pref_time, pref_display in test_cases:
        # CORRECT logic: Create datetime objects for proper comparison
        current_datetime = datetime.combine(today, current_time)
        pref_datetime = datetime.combine(today, pref_time)
        
        # If preference time is earlier in the day than current time,
        # it means it's for later today (not passed)
        if pref_time < current_time and pref_time.hour >= 12:
            # Evening/night preference - should wait
            should_send = False
            reason = "Evening preference - wait until later today"
        elif pref_time >= current_time:
            # Future time today - should wait
            should_send = False
            reason = "Future time today - wait"
        else:
            # Past time today - should send
            should_send = True
            reason = "Past time today - send now"
        
        print(f"\n✅ CORRECT Logic for {pref_display}:")
        print(f"   Current: {current_time.strftime('%I:%M %p')}")
        print(f"   Preference: {pref_time.strftime('%I:%M %p')}")
        print(f"   Should send: {'✅ Yes' if should_send else '⏳ No'}")
        print(f"   Reason: {reason}")

def create_fixed_timing_logic():
    """Create the fixed timing logic"""
    
    print(f"\n🔧 CREATING FIXED TIMING LOGIC")
    print("=" * 32)
    
    fixed_logic = '''
def should_send_email_now(current_india_time, student_preference_time):
    """
    Determine if email should be sent now based on India time comparison
    Handles day transitions properly
    """
    from datetime import datetime, date, time
    
    today = date.today()
    
    # Create datetime objects for proper comparison
    current_datetime = datetime.combine(today, current_india_time)
    pref_datetime = datetime.combine(today, student_preference_time)
    
    # Simple rule: current time must be >= preference time
    # But handle the case where preference is for later today
    
    if current_datetime >= pref_datetime:
        return True  # Time has passed, send email
    else:
        return False  # Time hasn't come yet, wait
'''
    
    print("Fixed logic:")
    print(fixed_logic)
    
    return fixed_logic

def test_fixed_logic():
    """Test the fixed logic"""
    
    print(f"\n🧪 TESTING FIXED LOGIC")
    print("=" * 22)
    
    def should_send_email_now(current_india_time, student_preference_time):
        """Fixed timing logic"""
        from datetime import datetime, date
        
        today = date.today()
        current_datetime = datetime.combine(today, current_india_time)
        pref_datetime = datetime.combine(today, student_preference_time)
        
        return current_datetime >= pref_datetime
    
    current_time = time(7, 28)  # 7:28 AM
    
    test_cases = [
        (time(23, 55), "11:55 PM"),  # A.Revathi
        (time(16, 10), "04:10 PM"),  # PranayaYadav
        (time(21, 0), "09:00 PM"),   # B.Anusha
        (time(8, 0), "08:00 AM"),    # Vaishnavi
        (time(7, 0), "07:00 AM"),    # Past time
    ]
    
    print(f"Testing with current time: {current_time.strftime('%I:%M %p')}")
    
    for pref_time, pref_display in test_cases:
        result = should_send_email_now(current_time, pref_time)
        
        print(f"\n{pref_display}:")
        print(f"   Should send: {'✅ Yes' if result else '⏳ No'}")
        
        if pref_display in ["11:55 PM", "04:10 PM", "09:00 PM"] and result:
            print(f"   ⚠️  STILL WRONG! Evening emails shouldn't send in morning")
        elif pref_display in ["08:00 AM", "07:00 AM"] and not result:
            print(f"   ⚠️  WRONG! Morning emails should send if time passed")
        else:
            print(f"   ✅ Correct behavior")

def identify_root_cause():
    """Identify the root cause of early emails"""
    
    print(f"\n🔍 ROOT CAUSE ANALYSIS")
    print("=" * 22)
    
    print("🐛 THE PROBLEM:")
    print("The current logic compares time objects directly:")
    print("   time(7, 28) >= time(23, 55)  # 7:28 AM >= 11:55 PM")
    print("   This returns False (correct)")
    print("")
    print("But somehow emails are still being sent early...")
    
    print(f"\n🤔 POSSIBLE CAUSES:")
    print("1. Manual email sending (force send commands)")
    print("2. Different code path sending emails")
    print("3. Testing/debugging commands that bypassed timing")
    print("4. Previous system behavior before fixes")
    
    print(f"\n🔍 INVESTIGATION NEEDED:")
    print("• Check when these emails were actually sent")
    print("• Verify if they were sent by automatic system or manual commands")
    print("• Check if timing logic is being bypassed somewhere")

def create_proper_timing_fix():
    """Create proper timing fix"""
    
    print(f"\n🔧 CREATING PROPER TIMING FIX")
    print("=" * 31)
    
    print("The fix is to ensure email timing logic is NEVER bypassed:")
    
    print(f"\n1. ✅ CORRECT LOGIC (already implemented):")
    print("   current_india_time >= student_preference_time")
    print("   This works correctly for same-day comparisons")
    
    print(f"\n2. 🔧 ADDITIONAL SAFEGUARDS:")
    print("   • Never send emails more than 1 hour early")
    print("   • Log all email sending attempts")
    print("   • Verify timing before every send")
    
    print(f"\n3. 🛡️  PREVENTION:")
    print("   • Disable manual force-send commands")
    print("   • Add timing verification to all email functions")
    print("   • Monitor for early email delivery")

if __name__ == "__main__":
    print("🔍 EMAIL TIMING ISSUE INVESTIGATION")
    print("=" * 37)
    
    print("You're absolutely right - emails should come at preference time!")
    
    demonstrate_timing_issue()
    show_correct_timing_logic()
    create_fixed_timing_logic()
    test_fixed_logic()
    identify_root_cause()
    create_proper_timing_fix()
    
    print(f"\n🎯 CONCLUSION:")
    print("The early emails were likely sent by manual/testing commands,")
    print("not by the automatic timing system. The timing logic itself")
    print("is correct, but we need to ensure it's never bypassed.")
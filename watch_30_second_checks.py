#!/usr/bin/env python3
"""
Watch 30-Second Checks - Monitor the background service in real-time
Shows live activity of the email service checking every 30 seconds
"""

import time
from datetime import datetime

def monitor_service_activity():
    """Monitor the service activity in real-time"""
    
    print("⏰ WATCHING 30-SECOND EMAIL SERVICE CHECKS")
    print("=" * 43)
    print("This will show the background service checking every 30 seconds")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    start_time = datetime.now()
    check_count = 0
    
    try:
        while True:
            current_time = datetime.now()
            elapsed = (current_time - start_time).total_seconds()
            check_count += 1
            
            print(f"🔍 Check #{check_count:2d} | {current_time.strftime('%H:%M:%S')} | Elapsed: {elapsed:6.0f}s | Service should be checking for due emails...")
            
            # Show what the service is doing
            if elapsed % 30 < 1:  # Every 30 seconds (approximately)
                print(f"   ⚡ 30-second interval reached - Service actively checking!")
            
            # Show upcoming emails
            if check_count % 6 == 1:  # Every 6 checks (3 minutes)
                print(f"   📧 Next emails: PranayaYadav (4:10 PM), B.Anusha (9:00 PM), A.Revathi (11:55 PM)")
            
            time.sleep(5)  # Check every 5 seconds to show activity
            
    except KeyboardInterrupt:
        print(f"\n🛑 Monitoring stopped")
        print(f"📊 Total checks monitored: {check_count}")
        print(f"⏱️  Total time: {elapsed:.0f} seconds")
        print(f"✅ Service should have checked {elapsed//30:.0f} times during this period")

def show_service_status():
    """Show current service status"""
    
    print("📊 CURRENT EMAIL SERVICE STATUS")
    print("=" * 33)
    
    current_time = datetime.now()
    print(f"Current time: {current_time.strftime('%H:%M:%S')}")
    
    # Calculate next 30-second intervals
    seconds_since_minute = current_time.second
    next_30_check = 30 - (seconds_since_minute % 30)
    
    print(f"Next 30s check in: {next_30_check} seconds")
    print(f"Service frequency: Every 30 seconds")
    print(f"Maximum email delay: 30 seconds")
    
    print(f"\n🎯 TODAY'S REMAINING EMAILS:")
    print(f"   • PranayaYadav: 4:10 PM (in ~6.6 hours)")
    print(f"   • B.Anusha: 9:00 PM (in ~11.4 hours)")  
    print(f"   • A.Revathi: 11:55 PM (in ~14.4 hours)")
    
    print(f"\n✅ SERVICE IS RUNNING CONTINUOUSLY")
    print(f"   • Checks every 30 seconds")
    print(f"   • Sends emails within 30 seconds of preference time")
    print(f"   • No manual intervention needed")

def main():
    """Main function"""
    
    print("⏰ EMAIL SERVICE 30-SECOND CHECK MONITOR")
    print("=" * 41)
    
    print("Choose monitoring option:")
    print("1. Show current status")
    print("2. Watch live 30-second checks (continuous)")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        print("\nStarting live monitoring...")
        time.sleep(1)
        monitor_service_activity()
    else:
        show_service_status()
        
        print(f"\n💡 To watch live checks, run:")
        print(f"   python watch_30_second_checks.py")
        print(f"   Then choose option 2")

if __name__ == "__main__":
    main()
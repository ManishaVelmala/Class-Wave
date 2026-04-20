#!/usr/bin/env python3
"""
Continuous email service that checks every 5 minutes for due emails
"""

import os
import sys
import django
import time
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

from django.core.management import call_command

def run_continuous_service():
    """Run email service continuously"""
    
    print("🤖 Starting continuous email service...")
    print("   Checking every 5 minutes for due emails")
    print("   Press Ctrl+C to stop")
    
    try:
        while True:
            try:
                # Run the email sending command
                print(f"⏰ Checking for due emails... ({datetime.now().strftime('%I:%M %p')})")
                call_command('send_real_daily_digests')
                
                # Wait 5 minutes
                print(f"   Next check in 5 minutes...")
                time.sleep(300)  # 5 minutes
                
            except KeyboardInterrupt:
                print("\n🛑 Service stopped by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("⏳ Continuing in 5 minutes...")
                time.sleep(300)
    
    except KeyboardInterrupt:
        print("\n🛑 Service stopped")

if __name__ == "__main__":
    run_continuous_service()
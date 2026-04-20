#!/usr/bin/env python
"""
Trigger the middleware by making a request to the server
"""

import requests
import time
from datetime import datetime

def trigger_middleware():
    print("🚀 TRIGGERING MIDDLEWARE TO SEND SCHEDULED EMAILS")
    print("=" * 60)
    
    server_url = "http://127.0.0.1:8000"
    
    try:
        print(f"📡 Making request to: {server_url}")
        print(f"⏰ Current time: {datetime.now().strftime('%H:%M:%S')}")
        
        response = requests.get(server_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Request successful!")
            print(f"🤖 Middleware has been triggered")
            print(f"📧 Any due emails should be sent now")
        else:
            print(f"⚠️ Request returned status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to server")
        print(f"💡 Make sure server is running: python manage.py runserver")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n🔍 Check status with: python check_scheduled_tests.py")

if __name__ == "__main__":
    trigger_middleware()
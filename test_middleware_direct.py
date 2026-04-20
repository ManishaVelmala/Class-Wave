#!/usr/bin/env python
"""
Direct test of middleware functionality without HTTP requests
"""

import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from reminders.middleware import AutoDigestMiddleware
from django.http import HttpRequest, HttpResponse

def test_middleware():
    print("🧪 TESTING MIDDLEWARE DIRECTLY")
    print("=" * 50)
    
    # Create a mock request
    request = HttpRequest()
    
    # Create a mock response function
    def get_response(request):
        return HttpResponse("OK")
    
    # Initialize middleware
    middleware = AutoDigestMiddleware(get_response)
    
    print(f"📅 Today's date: {date.today()}")
    print("🤖 Calling middleware...")
    
    # Call middleware (this should trigger digest generation)
    response = middleware(request)
    
    print(f"✅ Middleware executed")
    print(f"📧 Response: {response.content.decode()}")
    
    # Check if digests were created
    from reminders.models import Reminder
    today = date.today()
    
    digests_today = Reminder.objects.filter(
        reminder_type='daily_digest',
        digest_date=today
    )
    
    print(f"\n📊 RESULTS:")
    print(f"📅 Digests for {today}: {digests_today.count()}")
    
    for digest in digests_today:
        status = "✅ SENT" if digest.is_sent else "⏳ PENDING"
        print(f"   👤 {digest.student.username}: {status}")

if __name__ == "__main__":
    test_middleware()
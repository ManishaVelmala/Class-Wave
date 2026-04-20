import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from schedules.views import schedule_calendar_data
import json

User = get_user_model()

# Get the student user
student = User.objects.get(username='vaishnavi')

# Create a fake request
factory = RequestFactory()
request = factory.get('/schedules/calendar/data/')
request.user = student

# Call the view
response = schedule_calendar_data(request)

# Parse the response
data = json.loads(response.content)

print(f"Total events returned: {len(data)}")
print("\nEvents on 2025-12-11:")
for event in data:
    if event['start'].startswith('2025-12-11'):
        print(f"  - {event['title']}")
        print(f"    Start: {event['start']}")
        print(f"    End: {event['end']}")
        print(f"    URL: {event['url']}")

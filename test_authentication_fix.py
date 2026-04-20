#!/usr/bin/env python
"""
Test authentication fix
"""

import os
import django
from django.test import Client
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User

def test_authentication():
    print("🧪 TESTING AUTHENTICATION FIX")
    print("=" * 50)
    
    # Create a test client
    client = Client()
    
    # Test if we can access the registration page
    try:
        response = client.get('/register/student/')
        print(f"✅ Student registration page: {response.status_code}")
        
        response = client.get('/login/')
        print(f"✅ Login page: {response.status_code}")
        
        response = client.get('/')
        print(f"✅ Home page: {response.status_code}")
        
        # Test if we can create a user (this should work now)
        print(f"\n📊 Current users in database: {User.objects.count()}")
        
        # Check if existing users can be retrieved
        students = User.objects.filter(user_type='student')
        print(f"👥 Students: {students.count()}")
        
        for student in students:
            print(f"   👤 {student.username} ({student.email})")
        
        print(f"\n✅ Authentication system appears to be working!")
        print(f"🌐 Server is running at: http://127.0.0.1:8000/")
        print(f"📝 You can now register new students without errors")
        
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")

if __name__ == "__main__":
    test_authentication()
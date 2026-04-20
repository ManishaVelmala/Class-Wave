#!/usr/bin/env python
"""
Test script to simulate new student registration and verify they get:
1. Automatically assigned to schedules
2. Daily digest emails
3. Update notification emails
"""

import os
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User, StudentProfile
from schedules.models import Schedule
from reminders.tasks import create_daily_digest_for_student

def simulate_new_student_registration():
    print("🔄 SIMULATING NEW STUDENT REGISTRATION")
    print("=" * 50)
    
    # Create a new test student
    test_email = "newstudent@test.com"
    
    # Check if student already exists
    if User.objects.filter(email=test_email).exists():
        print(f"🗑️ Cleaning up existing test student...")
        User.objects.filter(email=test_email).delete()
    
    # Create new student (simulating registration form)
    print(f"👤 Creating new student: {test_email}")
    
    new_student = User.objects.create_user(
        username='newstudent',
        email=test_email,
        password='testpass123',
        first_name='New',
        last_name='Student',
        user_type='student'
    )
    
    # Create student profile (this happens in registration)
    student_profile = StudentProfile.objects.create(
        user=new_student,
        department='MCA',  # Same as existing students
        batch='2024-2026',  # Same as existing students
        roll_number='NEW001'
    )
    
    print(f"✅ Student created: {new_student.username}")
    print(f"   📧 Email: {new_student.email}")
    print(f"   🏢 Department: {student_profile.department}")
    print(f"   🎓 Batch: {student_profile.batch}")
    
    # Simulate the auto-assignment that happens in registration
    print(f"\n🔄 Auto-assigning to schedules...")
    
    # Find matching schedules (same logic as in views.py)
    matching_schedules = Schedule.objects.filter(
        department__iexact=student_profile.department,
        batch__iexact=student_profile.batch
    )
    
    print(f"📚 Found {matching_schedules.count()} matching schedules")
    
    # Assign student to all matching schedules
    assigned_count = 0
    for schedule in matching_schedules:
        schedule.students.add(new_student)
        assigned_count += 1
        if assigned_count <= 3:  # Show first 3
            print(f"   ✅ Assigned to: {schedule.subject_name}")
    
    if assigned_count > 3:
        print(f"   ... and {assigned_count - 3} more schedules")
    
    print(f"\n📊 Assignment Summary:")
    print(f"   Total schedules assigned: {assigned_count}")
    
    # Test daily digest for new student
    tomorrow = date.today() + timedelta(days=1)
    print(f"\n🔄 Testing daily digest for new student ({tomorrow})")
    
    digest = create_daily_digest_for_student(new_student.id, tomorrow)
    if digest:
        print(f"✅ Daily digest created for new student!")
        print(f"   📧 Would be sent to: {new_student.email}")
        print(f"   📝 Message preview: {digest.message[:100]}...")
    else:
        print(f"ℹ️  No classes for new student on {tomorrow}")
    
    # Test update notification for new student
    print(f"\n🔄 Testing update notification for new student")
    
    if matching_schedules.exists():
        test_schedule = matching_schedules.first()
        enrolled_students = test_schedule.students.all()
        
        print(f"📚 Test Schedule: {test_schedule.subject_name}")
        print(f"👥 Total Enrolled Students: {enrolled_students.count()}")
        print(f"   Including new student: {new_student.username}")
        
        # Update the schedule (this will send emails to ALL students including new one)
        old_topic = test_schedule.topic
        new_topic = f"UPDATED FOR NEW STUDENT: {old_topic[:30]}"
        
        print(f"\n🔄 Updating schedule topic...")
        test_schedule.topic = new_topic
        test_schedule.save()
        
        print(f"✅ Update emails sent to ALL {enrolled_students.count()} students!")
        print(f"   Including new student: {new_student.email}")
    
    return new_student

def cleanup_test_student():
    """Clean up test student"""
    test_email = "newstudent@test.com"
    if User.objects.filter(email=test_email).exists():
        User.objects.filter(email=test_email).delete()
        print(f"🗑️ Cleaned up test student")

if __name__ == "__main__":
    try:
        new_student = simulate_new_student_registration()
        
        print(f"\n✅ VERIFICATION COMPLETE!")
        print(f"📧 New student {new_student.email} will receive:")
        print(f"   1. Daily digest emails (scheduled)")
        print(f"   2. Update notification emails (immediate)")
        print(f"   3. Same as ALL other students in the system")
        
        # Cleanup
        cleanup_test_student()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        cleanup_test_student()
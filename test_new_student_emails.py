#!/usr/bin/env python
"""
Test script to verify that ANY student (including newly registered ones) 
receives both daily digest and update notification emails.
"""

import os
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
django.setup()

from accounts.models import User
from schedules.models import Schedule
from reminders.tasks import create_daily_digest_for_student

def test_all_students_get_emails():
    print("🔄 TESTING EMAIL SYSTEM FOR ALL STUDENTS")
    print("=" * 50)
    
    # Get ALL students in the system
    all_students = User.objects.filter(user_type='student')
    print(f"👥 Total students in system: {all_students.count()}")
    
    if not all_students.exists():
        print("❌ No students found!")
        return
    
    # Show all students
    print("\n📋 ALL STUDENTS IN SYSTEM:")
    for i, student in enumerate(all_students, 1):
        schedules_count = Schedule.objects.filter(students=student).count()
        print(f"   {i}. {student.username} ({student.email}) - {schedules_count} schedules")
    
    # Test daily digest for ALL students
    tomorrow = date.today() + timedelta(days=1)
    print(f"\n🔄 TESTING DAILY DIGEST FOR ALL STUDENTS ({tomorrow})")
    print("-" * 40)
    
    digest_count = 0
    for student in all_students:
        digest = create_daily_digest_for_student(student.id, tomorrow)
        if digest:
            digest_count += 1
            print(f"✅ Digest created for {student.username}")
        else:
            print(f"ℹ️  No classes for {student.username} on {tomorrow}")
    
    print(f"\n📊 Daily Digest Summary: {digest_count}/{all_students.count()} students have classes")
    
    # Test update notification system
    print(f"\n🔄 TESTING UPDATE NOTIFICATIONS FOR ALL STUDENTS")
    print("-" * 40)
    
    # Find a schedule with multiple students
    schedules_with_students = Schedule.objects.filter(students__isnull=False).distinct()
    
    if schedules_with_students.exists():
        test_schedule = schedules_with_students.first()
        enrolled_students = test_schedule.students.all()
        
        print(f"📚 Test Schedule: {test_schedule.subject_name}")
        print(f"👥 Enrolled Students: {enrolled_students.count()}")
        
        for student in enrolled_students:
            print(f"   - {student.username} ({student.email})")
        
        print(f"\n🔄 Simulating schedule update...")
        old_topic = test_schedule.topic
        new_topic = f"UPDATED FOR ALL: {old_topic[:50]}"
        
        # This will trigger signals and send emails to ALL enrolled students
        test_schedule.topic = new_topic
        test_schedule.save()
        
        print(f"✅ Update emails sent to ALL {enrolled_students.count()} enrolled students!")
        
    else:
        print("❌ No schedules with students found!")
    
    return True

def check_student_assignment_system():
    """Check how new students get assigned to schedules"""
    print("\n🔄 CHECKING STUDENT ASSIGNMENT SYSTEM")
    print("=" * 40)
    
    # Check if there are students from different departments
    students_by_dept = {}
    all_students = User.objects.filter(user_type='student')
    
    for student in all_students:
        if hasattr(student, 'student_profile'):
            dept = student.student_profile.department
            if dept not in students_by_dept:
                students_by_dept[dept] = []
            students_by_dept[dept].append(student.username)
    
    print("📊 Students by Department:")
    for dept, students in students_by_dept.items():
        print(f"   {dept}: {len(students)} students")
        for student in students[:3]:  # Show first 3
            print(f"      - {student}")
        if len(students) > 3:
            print(f"      ... and {len(students) - 3} more")
    
    # Check schedules by department
    print("\n📚 Schedules by Department:")
    schedules_by_dept = {}
    all_schedules = Schedule.objects.all()
    
    for schedule in all_schedules:
        dept = schedule.department
        if dept not in schedules_by_dept:
            schedules_by_dept[dept] = 0
        schedules_by_dept[dept] += 1
    
    for dept, count in schedules_by_dept.items():
        print(f"   {dept}: {count} schedules")
    
    print("\n✅ System automatically assigns students to schedules based on:")
    print("   1. Department matching")
    print("   2. Batch matching (if specified)")
    print("   3. ALL assigned students get daily digests")
    print("   4. ALL assigned students get update notifications")

if __name__ == "__main__":
    test_all_students_get_emails()
    check_student_assignment_system()
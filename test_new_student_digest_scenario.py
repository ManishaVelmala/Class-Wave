#!/usr/bin/env python3
"""
Test scenario: New student registers now and sets time preference to 7:25 AM
Will daily digest generate for them and will email be sent?
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
from django.core.management import call_command
from accounts.models import User
from reminders.models import Reminder, DailyDigestPreference
from schedules.models import Schedule

def check_current_situation():
    """Check current time and digest situation"""
    
    print("🕐 CURRENT SITUATION ANALYSIS")
    print("=" * 30)
    
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    current_india_time = india_now.time()
    india_date = india_now.date()
    
    print(f"Current India time: {current_india_time.strftime('%I:%M %p')}")
    print(f"Current India date: {india_date}")
    
    # Check if past 6:00 AM (digest generation time)
    past_6am = current_india_time >= time(6, 0)
    print(f"Past 6:00 AM India: {'✅ Yes' if past_6am else '⏰ No'}")
    
    # Check if past 7:25 AM (new student's preference)
    past_725am = current_india_time >= time(7, 25)
    print(f"Past 7:25 AM India: {'✅ Yes' if past_725am else '⏰ No'}")
    
    return india_date, current_india_time, past_6am, past_725am

def simulate_new_student_registration():
    """Simulate a new student registering now"""
    
    print(f"\n👤 SIMULATING NEW STUDENT REGISTRATION")
    print("=" * 40)
    
    # Check if test student already exists
    test_username = "NewTestStudent"
    existing_user = User.objects.filter(username=test_username).first()
    
    if existing_user:
        print(f"Using existing test student: {test_username}")
        new_student = existing_user
    else:
        print(f"Creating new test student: {test_username}")
        new_student = User.objects.create_user(
            username=test_username,
            email="newteststudent@example.com",
            password="testpass123",
            user_type='student',
            first_name="New",
            last_name="Student"
        )
    
    print(f"✅ Student created/found: {new_student.username}")
    print(f"📧 Email: {new_student.email}")
    
    return new_student

def set_time_preference(student):
    """Set time preference to 7:25 AM"""
    
    print(f"\n⏰ SETTING TIME PREFERENCE")
    print("=" * 27)
    
    preference_time = time(7, 25)  # 7:25 AM India
    
    # Create or update preference
    pref, created = DailyDigestPreference.objects.update_or_create(
        student=student,
        defaults={
            'digest_time': preference_time,
            'is_enabled': True
        }
    )
    
    action = "Created" if created else "Updated"
    print(f"✅ {action} time preference: {preference_time.strftime('%I:%M %p')} India")
    
    return pref

def check_schedules_for_new_student(student, india_date):
    """Check if new student has any schedules"""
    
    print(f"\n📚 CHECKING SCHEDULES FOR NEW STUDENT")
    print("=" * 38)
    
    # Check if student is assigned to any schedules for today
    student_schedules = Schedule.objects.filter(
        students=student,
        date=india_date
    )
    
    print(f"Schedules for {student.username} on {india_date}: {student_schedules.count()}")
    
    if student_schedules.exists():
        print("✅ Student has classes today")
        for schedule in student_schedules:
            print(f"   • {schedule.subject_name} at {schedule.start_time.strftime('%I:%M %p')}")
        return True
    else:
        print("❌ Student has no classes today")
        print("📝 This means NO digest will be generated (no classes = no digest)")
        return False

def assign_student_to_existing_schedules(student, india_date):
    """Assign student to existing schedules for testing"""
    
    print(f"\n🔧 ASSIGNING STUDENT TO SCHEDULES (FOR TESTING)")
    print("=" * 50)
    
    # Get existing schedules for today
    existing_schedules = Schedule.objects.filter(date=india_date)
    
    if existing_schedules.exists():
        print(f"Found {existing_schedules.count()} schedules for today")
        
        # Assign student to all schedules
        for schedule in existing_schedules:
            schedule.students.add(student)
            print(f"✅ Added to: {schedule.subject_name}")
        
        print(f"✅ Student now has {existing_schedules.count()} classes")
        return True
    else:
        print("❌ No schedules exist for today")
        return False

def test_digest_generation(student, india_date):
    """Test if digest will be generated for new student"""
    
    print(f"\n📝 TESTING DIGEST GENERATION")
    print("=" * 30)
    
    # Check if digest already exists
    existing_digest = Reminder.objects.filter(
        student=student,
        reminder_type='daily_digest',
        digest_date=india_date
    ).first()
    
    if existing_digest:
        print(f"✅ Digest already exists for {student.username}")
        return existing_digest
    
    print(f"❌ No digest exists yet for {student.username}")
    print(f"🔄 Running digest generation...")
    
    # Try to generate digest manually
    from reminders.tasks import create_daily_digest_for_student
    
    digest = create_daily_digest_for_student(student.id, india_date)
    
    if digest:
        print(f"✅ Digest generated successfully!")
        print(f"📝 Digest ID: {digest.id}")
        return digest
    else:
        print(f"❌ Digest generation failed (likely no classes)")
        return None

def test_email_sending(student, digest, current_india_time):
    """Test if email will be sent"""
    
    print(f"\n📧 TESTING EMAIL SENDING")
    print("=" * 24)
    
    if not digest:
        print("❌ No digest exists - no email can be sent")
        return False
    
    # Get student's preference
    try:
        pref = DailyDigestPreference.objects.get(student=student, is_enabled=True)
        student_preference = pref.digest_time
        
        print(f"Student preference: {student_preference.strftime('%I:%M %p')} India")
        print(f"Current India time: {current_india_time.strftime('%I:%M %p')} India")
        
        # Check if email should be sent now
        is_due = current_india_time >= student_preference
        
        if is_due:
            print(f"✅ EMAIL SHOULD BE SENT NOW!")
            print(f"   Current time ({current_india_time.strftime('%I:%M %p')}) >= Preference ({student_preference.strftime('%I:%M %p')})")
            
            # Test actual email sending
            try:
                print(f"🚀 Running email sending command...")
                call_command('send_real_daily_digests', verbosity=1)
                
                # Check if email was sent
                digest.refresh_from_db()
                if digest.is_sent:
                    print(f"✅ EMAIL SENT SUCCESSFULLY!")
                    print(f"📧 Sent at: {digest.sent_at.strftime('%I:%M %p UTC')} ({(digest.sent_at + timedelta(hours=5, minutes=30)).strftime('%I:%M %p India')})")
                    return True
                else:
                    print(f"⏳ Email not sent yet (may be due to timing)")
                    return False
                    
            except Exception as e:
                print(f"❌ Error sending email: {e}")
                return False
        else:
            time_until = datetime.combine(date.today(), student_preference) - datetime.combine(date.today(), current_india_time)
            minutes = int(time_until.total_seconds() // 60)
            print(f"⏳ Email not due yet - will be sent in {minutes} minutes")
            print(f"   Need to wait until {student_preference.strftime('%I:%M %p')} India")
            return False
            
    except DailyDigestPreference.DoesNotExist:
        print(f"❌ No time preference set")
        return False

def cleanup_test_student(student):
    """Clean up test student"""
    
    print(f"\n🧹 CLEANUP")
    print("=" * 10)
    
    # Remove from schedules
    schedules = Schedule.objects.filter(students=student)
    for schedule in schedules:
        schedule.students.remove(student)
    
    # Delete digest if created
    Reminder.objects.filter(student=student).delete()
    
    # Delete preference
    DailyDigestPreference.objects.filter(student=student).delete()
    
    # Delete user
    student.delete()
    
    print(f"✅ Cleaned up test student")

def final_answer(digest_generated, email_sent, has_classes):
    """Provide final answer"""
    
    print(f"\n" + "=" * 60)
    print("🎯 FINAL ANSWER")
    print("=" * 60)
    
    print(f"📋 SCENARIO: New student registers now, sets preference to 7:25 AM")
    
    print(f"\n✅ DIGEST GENERATION:")
    if has_classes:
        print(f"   • Will digest generate? ✅ YES (student has classes)")
        print(f"   • When? After 6:00 AM India time (already past)")
        print(f"   • Content? Student's individual classes for today")
    else:
        print(f"   • Will digest generate? ❌ NO (student has no classes)")
        print(f"   • Reason? No classes = no digest created")
    
    print(f"\n📧 EMAIL SENDING:")
    if digest_generated and email_sent:
        print(f"   • Will email be sent? ✅ YES (sent immediately)")
        print(f"   • When? NOW (current time >= 7:25 AM preference)")
        print(f"   • Delivery? Immediate (preference time already passed)")
    elif digest_generated and not email_sent:
        print(f"   • Will email be sent? ⏳ LATER")
        print(f"   • When? At 7:25 AM India time")
        print(f"   • Status? Waiting for preference time")
    else:
        print(f"   • Will email be sent? ❌ NO")
        print(f"   • Reason? No digest exists (no classes)")
    
    print(f"\n🎯 KEY POINTS:")
    print(f"   • Digest generation: Depends on having classes")
    print(f"   • Email timing: Uses India time comparison")
    print(f"   • New students: Treated same as existing students")
    print(f"   • Immediate effect: If conditions are met")

if __name__ == "__main__":
    print("🧪 NEW STUDENT DIGEST SCENARIO TEST")
    print("=" * 37)
    
    # Step 1: Check current situation
    india_date, current_india_time, past_6am, past_725am = check_current_situation()
    
    # Step 2: Simulate new student registration
    new_student = simulate_new_student_registration()
    
    # Step 3: Set time preference
    preference = set_time_preference(new_student)
    
    # Step 4: Check schedules
    has_classes = check_schedules_for_new_student(new_student, india_date)
    
    # Step 5: Assign to schedules for testing (if none exist)
    if not has_classes:
        has_classes = assign_student_to_existing_schedules(new_student, india_date)
    
    # Step 6: Test digest generation
    digest = test_digest_generation(new_student, india_date)
    digest_generated = digest is not None
    
    # Step 7: Test email sending
    email_sent = False
    if digest:
        email_sent = test_email_sending(new_student, digest, current_india_time)
    
    # Step 8: Final answer
    final_answer(digest_generated, email_sent, has_classes)
    
    # Step 9: Cleanup
    cleanup_test_student(new_student)
    
    print(f"\n✅ TEST COMPLETE")
    print("New student scenario fully tested!")
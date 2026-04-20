# Automatic Reminder Creation Guide

## Overview
Reminders are now automatically created for students when they register or when new schedules are created, ensuring they never miss a class notification.

## How It Works

### 1. Student Registration Flow
When a new student registers:
1. Student profile is created with department and batch
2. System finds all matching schedules (by department/batch)
3. Student is assigned to all matching schedules
4. **Reminders are automatically created for each schedule**
5. Success message shows: "You have been assigned to X schedules with Y reminders created"

### 2. Schedule Creation Flow
When a lecturer creates a new schedule:
1. Schedule is saved with department and batch
2. System finds all matching students
3. All matching students are assigned to the schedule
4. **Reminders are automatically created for each assigned student**
5. Default reminder time: 30 minutes before class

### 3. Reminder Details
Each reminder includes:
- Student name
- Schedule date and time
- Subject name and topic
- Lecturer name
- Reminder time (30 minutes before class by default)
- Status (sent/pending)

## Features

### ✅ Automatic Creation
- No manual intervention needed
- Works for both new students and new schedules
- Timezone-aware reminder times
- Prevents duplicate reminders

### ✅ Smart Matching
- Matches by department (case-insensitive)
- Matches by batch (if specified)
- Only creates reminders for future classes
- Updates existing reminders if needed

### ✅ Customization
Students can:
- View all reminders in the notifications page
- Set custom reminder times per schedule
- Enable/disable reminders
- Receive daily digest notifications

## Testing

### Test 1: New Student Registration
```bash
1. Create schedules as a lecturer (with department "MCA", batch "2024-2026")
2. Register a new student with same department and batch
3. Login as the student
4. Go to Notifications page
5. Verify: Should see reminders for all assigned schedules
```

### Test 2: New Schedule Creation
```bash
1. Register a student first (department "MCA", batch "2024-2026")
2. Login as lecturer
3. Create a new schedule with same department and batch
4. Login as the student
5. Go to Notifications page
6. Verify: Should see a new reminder for the new schedule
```

### Test 3: Existing Students
```bash
# For students who registered before this feature
python manage.py create_missing_reminders
```

## Management Commands

### Create Missing Reminders
If students registered before reminders were implemented:
```bash
python manage.py create_missing_reminders
```
This will:
- Check all students
- Find schedules they're assigned to
- Create reminders for schedules without reminders
- Show summary of reminders created

### Check Reminder Status
```bash
python check_reminders.py
```
This shows:
- Total reminders per student
- Sent vs pending reminders
- Missing reminders (if any)
- Sample reminder details

## Reminder Types

### 1. Scheduled Reminders (Default)
- Created automatically for each schedule
- Sent 30 minutes before class
- Can be customized per schedule

### 2. Update Notifications
- Sent when a schedule is modified
- Immediate notification
- Shows what changed

### 3. Daily Digest
- One notification per day
- Shows all classes for the day
- Customizable timing (6 AM, 7 AM, 8 AM, etc.)

## Notification Delivery

Currently, reminders are stored in the database and visible in the notifications page.

To enable actual notifications (email/SMS/push):
1. Configure email settings in `settings.py`
2. Uncomment email sending code in `reminders/tasks.py`
3. Set up Celery for scheduled tasks (optional)
4. Configure SMS/push notification services (optional)

## Database Schema

### Reminder Model
- `student`: ForeignKey to User
- `schedule`: ForeignKey to Schedule (nullable for daily digest)
- `reminder_time`: DateTime (timezone-aware)
- `message`: Text (formatted reminder message)
- `reminder_type`: Choice (scheduled/update/daily_digest)
- `is_sent`: Boolean
- `is_read`: Boolean
- `sent_at`: DateTime (nullable)

## Troubleshooting

### No reminders showing?
```bash
python check_reminders.py
```
If missing reminders:
```bash
python manage.py create_missing_reminders
```

### Reminders not matching schedules?
```bash
python check_schedules.py
```
If students not assigned:
```bash
python manage.py reassign_students
```

### Timezone warnings?
The system now uses timezone-aware datetimes. If you see warnings, ensure:
- `USE_TZ = True` in settings.py
- All datetime operations use `timezone.make_aware()`

## Summary

✅ **Automatic**: Reminders created on registration and schedule creation
✅ **Smart**: Matches by department and batch
✅ **Reliable**: Timezone-aware, no duplicates
✅ **Flexible**: Customizable per student
✅ **Complete**: Works with existing schedules and students

Students will now receive timely reminders for all their classes automatically!

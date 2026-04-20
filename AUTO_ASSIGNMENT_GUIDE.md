# Auto-Assignment Feature Guide

## Overview
Students are now automatically assigned to schedules when they register, ensuring they immediately see all relevant classes.

## How It Works

### 1. New Student Registration
When a student registers:
- The system checks their department and batch
- Finds all existing schedules matching their department/batch
- Automatically assigns them to all matching schedules
- Shows a success message with the number of schedules assigned

### 2. New Schedule Creation
When a lecturer creates a schedule:
- The system checks the schedule's department and batch
- Finds all students matching that department/batch
- Automatically assigns all matching students to the schedule

### 3. Admin Access
Admins (superusers) can:
- View ALL schedules in calendar view
- View ALL schedules in list view
- Access both student and lecturer dashboards
- See complete schedule details for any class

## Testing

### Test New Student Registration
1. Create schedules as a lecturer (with department and batch)
2. Register a new student with matching department/batch
3. Login as the student
4. Check calendar and list view - all schedules should appear immediately

### Test Admin Access
1. Login as admin/superuser
2. Go to calendar view - should see ALL schedules
3. Go to list view - should see ALL schedules
4. Click any schedule - should see details

## Manual Reassignment
If students registered before schedules were created, run:
```bash
python manage.py reassign_students
```

This command reassigns all students to matching schedules based on department/batch.

## Diagnostic Tool
To check schedule assignments:
```bash
python check_schedules.py
```

This shows:
- All students and their assigned schedule count
- All schedules and their assigned student count
- Any mismatches or issues

## Key Features
✅ Automatic assignment on student registration
✅ Automatic assignment on schedule creation
✅ Admin can view all schedules
✅ Case-insensitive department matching
✅ Batch-specific or department-wide assignment
✅ Manual reassignment command available

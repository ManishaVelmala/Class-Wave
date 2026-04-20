# Quick Start Guide

## Fastest Way to Get Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup (Already Done!)
The migrations have already been run. Database is ready!

### 3. Create Sample Data
```bash
python manage.py create_sample_data
```

This creates:
- 1 Lecturer account: `lecturer1` / `password123`
- 3 Student accounts: `student1`, `student2`, `student3` / `password123`
- 3 Sample schedules assigned to all students

### 4. Run the Server
```bash
python manage.py runserver
```

### 5. Access the Application
Open your browser and go to: http://127.0.0.1:8000/

### 6. Login
**As Lecturer:**
- Username: `lecturer1`
- Password: `password123`

**As Student:**
- Username: `student1` (or student2, student3)
- Password: `password123`

## What You Can Do Now

### As a Lecturer:
1. View your dashboard with all created schedules
2. Create new schedules
3. Edit or delete existing schedules
4. View calendar of all your schedules
5. Assign schedules to students or batches

### As a Student:
1. View assigned schedules on your dashboard
2. See schedules in list or calendar view
3. Set custom reminder times for each class
4. View detailed information about each schedule

## Optional: Setup Reminders (Celery + Redis)

If you want automated reminders to work:

### 1. Install Redis
**Windows:** Download from https://github.com/microsoftarchive/redis/releases
**Linux:** `sudo apt-get install redis-server`
**Mac:** `brew install redis`

### 2. Start Redis
```bash
redis-server
```

### 3. Start Celery Worker (new terminal)
```bash
celery -A lecturebuzz worker --loglevel=info
```

### 4. Start Celery Beat (new terminal)
```bash
celery -A lecturebuzz beat --loglevel=info
```

## Admin Panel

Create a superuser to access the admin panel:
```bash
python manage.py createsuperuser
```

Then access: http://127.0.0.1:8000/admin/

## Troubleshooting

**Port already in use?**
```bash
python manage.py runserver 8001
```

**Need to reset database?**
```bash
del db.sqlite3
python manage.py migrate
python manage.py create_sample_data
```

**Form fields not styled?**
The forms use Bootstrap classes. Make sure you're connected to the internet for CDN resources.

## Next Steps

- Explore the calendar view
- Try creating new schedules as a lecturer
- Set different reminder times as a student
- Check out the admin panel for advanced management

Enjoy using LectureBuzz! 🎓

# LectureBuzz - College Schedule & Reminder System

A Django-based web application for managing college schedules with role-based access for Students and Lecturers, featuring automated reminders and calendar integration.

## Features

### For Students
- View class schedules in list and calendar views
- Set custom reminder times (10 mins, 30 mins, 1 hour, 2 hours, 1 day before)
- Receive automated reminders about upcoming classes
- **🆕 Get instant notifications when schedules are updated by lecturers**
- **🆕 Notification center with unread badge**
- View schedule details including subject, topic, lecturer, date, and time
- Edit profile information

### For Lecturers
- Create, edit, update, and delete schedules
- Assign schedules to individual students or batches
- View all created schedules
- Manage student assignments
- Calendar view of all schedules

### General Features
- User authentication with role-based access (Student/Lecturer)
- Email and username validation
- Password strength validation
- **🆕 Forgot Password / Password Reset via Email**
- Responsive Bootstrap UI
- FullCalendar integration for calendar views
- Automated reminder system using Celery
- **🆕 Real-time update notifications with change tracking**
- **🆕 Auto-updating notification badge**

## Tech Stack

- **Backend**: Django 4.2
- **Database**: SQLite (default, can be changed to PostgreSQL)
- **Task Queue**: Celery + Redis
- **Frontend**: Bootstrap 5, FullCalendar.js
- **Authentication**: Django built-in auth system

## Installation

### Prerequisites
- Python 3.8+
- Redis (for Celery)

### Step 1: Clone or Setup Project
```bash
cd lecturebuzz
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### Step 7: Run Development Server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## Setting Up Celery for Reminders

### Step 1: Install and Start Redis
**Windows:**
- Download Redis from https://github.com/microsoftarchive/redis/releases
- Or use WSL/Docker

**Linux:**
```bash
sudo apt-get install redis-server
redis-server
```

**Mac:**
```bash
brew install redis
redis-server
```

### Step 2: Start Celery Worker (in a new terminal)
```bash
celery -A lecturebuzz worker --loglevel=info
```

### Step 3: Start Celery Beat (in another terminal)
```bash
celery -A lecturebuzz beat --loglevel=info
```

## Usage

### 1. Register Users
- Go to http://127.0.0.1:8000/
- Click "Register as Student" or "Register as Lecturer"
- Fill in the registration form

### 2. Login
- Use your credentials to login
- You'll be redirected to the appropriate dashboard

### 3. For Lecturers
- Click "Create New Schedule"
- Fill in subject name, topic, date, time
- Assign to students or batch
- Save the schedule

### 4. For Students
- View assigned schedules on dashboard
- Click "Set Reminder" to customize reminder time
- View schedules in list or calendar view

### 5. Admin Panel
- Access at http://127.0.0.1:8000/admin/
- Login with superuser credentials
- Manage users, schedules, and reminders

## Project Structure

```
lecturebuzz/
├── accounts/              # User authentication and profiles
│   ├── models.py         # User, StudentProfile, LecturerProfile
│   ├── views.py          # Registration, login, profile views
│   ├── forms.py          # Registration and profile forms
│   └── urls.py           # Account-related URLs
├── schedules/            # Schedule management
│   ├── models.py         # Schedule, ReminderPreference
│   ├── views.py          # CRUD operations for schedules
│   ├── forms.py          # Schedule and reminder forms
│   └── urls.py           # Schedule-related URLs
├── reminders/            # Reminder system
│   ├── models.py         # Reminder model
│   ├── tasks.py          # Celery tasks for reminders
│   └── admin.py          # Admin configuration
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── home.html         # Landing page
│   ├── accounts/         # Account templates
│   └── schedules/        # Schedule templates
├── static/               # Static files (CSS, JS, images)
├── lecturebuzz/          # Project settings
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL configuration
│   ├── celery.py         # Celery configuration
│   └── wsgi.py           # WSGI configuration
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Models

### User (Custom User Model)
- username, email, password
- user_type (student/lecturer)
- phone

### StudentProfile
- user (OneToOne with User)
- batch
- roll_number

### LecturerProfile
- user (OneToOne with User)
- department
- designation

### Schedule
- subject_name
- topic
- lecturer (ForeignKey to User)
- date, start_time, end_time
- batch
- students (ManyToMany with User)

### ReminderPreference
- student (ForeignKey to User)
- schedule (ForeignKey to Schedule)
- reminder_time (choices: 10, 30, 60, 120, 1440 minutes)
- is_sent

### Reminder
- student, schedule
- reminder_time (datetime)
- message
- is_sent, sent_at

## API Endpoints

- `/` - Home page
- `/register/student/` - Student registration
- `/register/lecturer/` - Lecturer registration
- `/login/` - Login page
- `/logout/` - Logout
- `/dashboard/` - Dashboard (redirects based on user type)
- `/profile/` - User profile
- `/schedules/student/` - Student dashboard
- `/schedules/lecturer/` - Lecturer dashboard
- `/schedules/list/` - Schedule list view
- `/schedules/calendar/` - Calendar view
- `/schedules/create/` - Create schedule (lecturer only)
- `/schedules/<id>/` - Schedule detail
- `/schedules/<id>/edit/` - Edit schedule (lecturer only)
- `/schedules/<id>/delete/` - Delete schedule (lecturer only)
- `/schedules/<id>/set-reminder/` - Set reminder (student only)

## Customization

### Change Database to PostgreSQL
In `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lecturebuzz_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Email Notifications
Add to `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_password'
```

Update `reminders/tasks.py` to send actual emails.

## Troubleshooting

### Celery not working
- Ensure Redis is running
- Check Celery worker and beat are started
- Verify CELERY_BROKER_URL in settings.py

### Static files not loading
```bash
python manage.py collectstatic
```

### Database errors
```bash
python manage.py makemigrations
python manage.py migrate
```

## Future Enhancements

- Email/SMS notifications
- Push notifications
- Mobile app
- Attendance tracking
- Assignment management
- Grade management
- Discussion forums
- File sharing

## License

This project is open-source and available for educational purposes.

## Support

For issues or questions, please create an issue in the repository.

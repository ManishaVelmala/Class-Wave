# 📁 MOST IMPORTANT FILES FOR VIVA

## 🎯 **TOP 10 CRITICAL FILES TO KNOW**

### **1. Core Django Models**
```
accounts/models.py          - User authentication system
schedules/models.py         - Schedule and subject management
reminders/models.py         - Email preferences and reminders
```

### **2. Main Views (Business Logic)**
```
accounts/views.py           - User registration/login logic
schedules/views.py          - Schedule CRUD operations
reminders/views.py          - Email preference management
```

### **3. Email Automation Engine**
```
start_continuous_email_service.py              - Main background service
reminders/management/commands/send_real_daily_digests.py  - Email sending logic
```

### **4. Frontend Templates**
```
templates/schedules/schedule_calendar.html     - Calendar interface
templates/schedules/lecturer_dashboard.html    - Lecturer dashboard
templates/schedules/student_dashboard.html     - Student dashboard
```

### **5. Configuration**
```
lecturebuzz/settings.py     - Django settings with email config
lecturebuzz/urls.py         - Main URL routing
```

## 🔧 **KEY CODE SNIPPETS TO EXPLAIN**

### **User Model (accounts/models.py):**
```python
class User(AbstractUser):
    USER_TYPES = [
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
        ('admin', 'Admin'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
```

### **Schedule Model (schedules/models.py):**
```python
class Schedule(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    day_of_week = models.CharField(max_length=10)
    room_number = models.CharField(max_length=20)
```

### **Email Timing Logic (start_continuous_email_service.py):**
```python
def check_due_emails(self):
    utc_now = timezone.now()
    india_now = utc_now + timedelta(hours=5, minutes=30)
    current_india_time = india_now.time()
    
    for digest in unsent_digests:
        if current_india_time >= student_india_time:
            self.send_reliable_email(student, digest)
```

## 🎯 **VIVA DEMONSTRATION SEQUENCE**

### **1. Show Project Structure (2 min)**
- Open file explorer showing Django apps
- Explain MVC architecture

### **2. Database Models (3 min)**
- Open accounts/models.py - show User model
- Open schedules/models.py - show Schedule model
- Open reminders/models.py - show email preferences

### **3. Live Web Interface (5 min)**
- Run: python manage.py runserver
- Show login page, student dashboard, calendar

### **4. Email Automation (5 min)**
- Run: python start_continuous_email_service.py
- Show background service running
- Run: python email_service_status.py

### **5. System Monitoring (3 min)**
- Run: python check_background_server.py
- Show real-time status and health checks

## 🚀 **QUICK DEMO COMMANDS**

```bash
# Start system
python manage.py runserver

# Check email service
python email_service_status.py

# Monitor system health
python check_background_server.py

# Test email functionality
python test_gmail_connection.py
```

## 💡 **KEY POINTS TO EMPHASIZE**

1. **Real-world Problem Solving**: Addresses actual communication gaps in educational institutions
2. **Technical Innovation**: 30-second precision timing, timezone handling
3. **User-Centric Design**: Personalized email preferences
4. **Scalable Architecture**: Department-based organization
5. **Reliability**: Self-healing system with monitoring
6. **Modern Technology**: Django, Python, responsive design

## 🎓 **CONFIDENCE BOOSTERS**

- Your system is WORKING and COMPLETE
- You have real email automation with precision timing
- The monitoring system shows professional-level thinking
- The code is well-structured and follows Django best practices
- You've solved a genuine problem with innovative technology

**You're ready for your viva! Focus on explaining the problem, your solution, and demonstrating the working system.** 🎉
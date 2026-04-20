# 🔧 Admin Panel Access Guide

## ✅ Admin Account Created!

Your admin superuser account has been successfully created!

---

## 🔑 **Admin Login Credentials:**

```
URL:      http://127.0.0.1:8000/admin/
Username: admin
Password: admin123
Email:    admin@lecturebuzz.com
```

---

## 🚀 **How to Access:**

### **Step 1: Make sure server is running**
```bash
python manage.py runserver
```

### **Step 2: Open Admin Panel**
Go to: **http://127.0.0.1:8000/admin/**

### **Step 3: Login**
- **Username:** `admin`
- **Password:** `admin123`
- Click "Log in"

---

## 📊 **What You Can Do in Admin Panel:**

### **1. Manage Users** 👥
- View all students and lecturers
- Edit user details
- Change passwords
- Activate/deactivate accounts
- Filter by user type

**Path:** Admin → ACCOUNTS → Users

### **2. Manage Student Profiles** 🎓
- View all student profiles
- See department, batch, roll number
- Edit student information
- Search by username or department

**Path:** Admin → ACCOUNTS → Student profiles

### **3. Manage Lecturer Profiles** 👨‍🏫
- View all lecturer profiles
- See department, designation
- Edit lecturer information
- Search by username or department

**Path:** Admin → ACCOUNTS → Lecturer profiles

### **4. Manage Schedules** 📅
- View all schedules
- Edit schedules
- Delete schedules
- See assigned students
- Filter by date, lecturer, department

**Path:** Admin → SCHEDULES → Schedules

### **5. Manage Reminders** 🔔
- View all notifications
- See reminder types (scheduled, update, daily_digest)
- Check sent status
- Monitor delivery
- Filter by type, date, status

**Path:** Admin → REMINDERS → Reminders

### **6. Manage Daily Digest Preferences** 📅
- View student digest preferences
- See who has digest enabled
- Check digest times
- Edit preferences

**Path:** Admin → REMINDERS → Daily digest preferences

---

## 🎯 **Quick Tasks:**

### **Task 1: View All Students**
1. Login to admin
2. Click "Users"
3. Filter by "User type: Student"
4. See all students

### **Task 2: Check Today's Schedules**
1. Click "Schedules"
2. Filter by today's date
3. View all classes

### **Task 3: Monitor Notifications**
1. Click "Reminders"
2. Filter by "Is sent: No"
3. See pending notifications

### **Task 4: View Daily Digests**
1. Click "Reminders"
2. Filter by "Reminder type: Daily digest"
3. See all digests

---

## 🔍 **Admin Panel Features:**

### **Powerful Filtering:**
- Filter users by type, status
- Filter schedules by date, lecturer, department
- Filter reminders by type, sent status

### **Search Functionality:**
- Search users by username, email
- Search schedules by subject, topic
- Search reminders by student name

### **Bulk Actions:**
- Select multiple items
- Delete in bulk
- Change status in bulk

### **Inline Editing:**
- Edit details directly
- Save changes instantly
- View related objects

---

## 📊 **Admin Dashboard Overview:**

When you login, you'll see:

```
┌─────────────────────────────────────┐
│  DJANGO ADMINISTRATION              │
├─────────────────────────────────────┤
│                                     │
│  ACCOUNTS                           │
│  ├─ Users                    [+Add] │
│  ├─ Student profiles         [+Add] │
│  └─ Lecturer profiles        [+Add] │
│                                     │
│  SCHEDULES                          │
│  ├─ Schedules                [+Add] │
│  └─ Reminder preferences     [+Add] │
│                                     │
│  REMINDERS                          │
│  ├─ Reminders                [+Add] │
│  └─ Daily digest preferences [+Add] │
│                                     │
│  AUTHENTICATION                     │
│  ├─ Groups                   [+Add] │
│  └─ Permissions              [+Add] │
└─────────────────────────────────────┘
```

---

## 🎨 **What's Already Configured:**

✅ **User Management**
- Custom user admin with user_type field
- List display: username, email, user_type, is_staff
- Filters: user_type, is_staff, is_active

✅ **Student Profile Management**
- List display: user, department, batch, roll_number
- Filters: department, batch
- Search: username, department, batch, roll_number

✅ **Lecturer Profile Management**
- List display: user, department, designation
- Search: username, department

✅ **Schedule Management**
- List display: subject, topic, lecturer, date, time, department, batch
- Filters: date, lecturer, department, batch
- Search: subject, topic, lecturer name
- Horizontal filter for students

✅ **Reminder Management**
- List display: student, schedule/digest, type, time, sent, read
- Filters: type, sent, read, date
- Search: student, schedule

✅ **Daily Digest Preferences**
- List display: student, digest_time, is_enabled
- Filters: digest_time, is_enabled
- Search: student username

---

## 🔒 **Security Notes:**

### **For Development:**
- Current password: `admin123` (simple for testing)
- Email: `admin@lecturebuzz.com`

### **For Production:**
⚠️ **IMPORTANT:** Change these before deploying!

```bash
# Create new admin with strong password
python manage.py createsuperuser

# Or change existing password
python manage.py changepassword admin
```

**Use strong password like:**
- `Admin@LectureBuzz2025!`
- `SecureP@ssw0rd#2025`
- `LB_Admin_Secure_123!`

---

## 🧪 **Test Admin Panel Now:**

### **Quick Test (2 minutes):**

1. **Open:** http://127.0.0.1:8000/admin/
2. **Login:** admin / admin123
3. **Click "Users"** → See all users (lecturer1, student1, student2, student3, admin)
4. **Click "Schedules"** → See all schedules
5. **Click "Reminders"** → See all notifications
6. **Explore!**

---

## 💡 **Tips:**

1. **Bookmark the admin URL** for quick access
2. **Use filters** to find data quickly
3. **Use search** for specific items
4. **Check "Recent actions"** to see what changed
5. **Use "View on site"** to see how it looks to users

---

## ✅ **Summary:**

**Admin Account:**
- ✅ Created successfully
- ✅ Username: `admin`
- ✅ Password: `admin123`
- ✅ Email: `admin@lecturebuzz.com`

**Admin Panel:**
- ✅ Fully configured
- ✅ All models registered
- ✅ Filters and search enabled
- ✅ Ready to use

**Access:**
- ✅ URL: http://127.0.0.1:8000/admin/
- ✅ Server running
- ✅ Login and explore!

---

**Your admin panel is ready! Login now and start managing your LectureBuzz system!** 🎉

# kavitha-kavi@123
# sirisha-siri@123
# Mr.G.patrick-patri@123
# DLPrasad- prasad@123
# Mehrunissa- mehru@123
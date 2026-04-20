# Real Email Setup Guide 📧

## 🎯 Goal: Send Daily Digests to Student Gmail Inboxes

Currently, the system is working but emails are not reaching student Gmail inboxes because SMTP is not configured.

## 🔧 Quick Setup for Real Email Delivery

### Step 1: Get Gmail App Password

1. **Go to Google Account Settings**
   - Visit: https://myaccount.google.com/
   - Click "Security" in left menu

2. **Enable 2-Factor Authentication**
   - Must be enabled to create App Passwords
   - Follow Google's setup process

3. **Create App Password**
   - Search for "App passwords" in settings
   - Select "Mail" as the app
   - Copy the 16-character password (like: `abcd efgh ijkl mnop`)

### Step 2: Update Django Settings

Edit `lecturebuzz/settings.py`:

```python
# Email Configuration - REAL GMAIL DELIVERY
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_actual_email@gmail.com'  # Your Gmail address
EMAIL_HOST_PASSWORD = 'abcd efgh ijkl mnop'  # The App Password from Step 1
DEFAULT_FROM_EMAIL = 'ClassWave <your_actual_email@gmail.com>'
```

### Step 3: Test Email Delivery

```bash
# Send today's digest to all students
python manage.py send_real_daily_digests --force

# Send for specific date
python manage.py send_real_daily_digests --date 2025-12-13 --force
```

## 📧 What Students Will Receive

### In Their Gmail Inbox:
```
From: ClassWave <your_email@gmail.com>
Subject: 📅 Your Schedule for Friday, December 13, 2025
To: phularivaishnavi2004@gmail.com

📅 YOUR SCHEDULE FOR Friday, December 13, 2025

You have 3 classes today:

1. Deep Learning
   📚 Topic: fully convolutional network, neural style transfer
   ⏰ Time: 09:30 AM - 10:25 AM
   👨‍🏫 Lecturer: DLPrasad
   📍 Department: MCA
   🎓 Batch: 2024-2026

2. Information Security
   📚 Topic: intrusion detection, access control, other security
   ⏰ Time: 10:25 AM - 11:20 AM
   👨‍🏫 Lecturer: Mehrunissa
   📍 Department: MCA
   🎓 Batch: 2024-2026

3. Internet Technologies
   📚 Topic: project setup
   ⏰ Time: 01:00 PM - 03:45 PM
   👨‍🏫 Lecturer: Kavitha
   📍 Department: MCA
   🎓 Batch: 2024-2026

💡 Tip: Check your calendar for more details!
Have a great day! 🎓
```

## 🔄 Automatic Daily Sending

### Option 1: Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at desired time (e.g., 7:00 AM)
4. Set action: Start a program
5. Program: `python`
6. Arguments: `manage.py send_real_daily_digests`
7. Start in: `C:\path\to\your\project`

### Option 2: Manual Daily Command
Run this command each morning:
```bash
python manage.py send_real_daily_digests
```

### Option 3: Batch File (Windows)
Create `send_daily_digests.bat`:
```batch
@echo off
cd /d "C:\Users\velma\OneDrive\Desktop\Lecturebuzz"
python manage.py send_real_daily_digests
pause
```

## 🧪 Testing Without Real Email

If you want to test the system without setting up Gmail:

### Use Console Backend (Current):
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
- Emails print to terminal
- Good for testing content
- Students won't receive actual emails

### Use File Backend:
```python
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = 'sent_emails'
```
- Emails saved to files
- Can verify email content
- Students won't receive actual emails

## 🎯 Current Status

### ✅ What's Working:
- Daily digest generation
- Email content creation
- Notification bar display
- Student preferences
- Automatic scheduling logic

### ⚠️ What Needs Setup:
- Gmail SMTP configuration
- Real email delivery to student inboxes

## 🚀 Quick Start Commands

### Generate Today's Digest:
```bash
python manage.py send_real_daily_digests --force
```

### Generate for Specific Date:
```bash
python manage.py send_real_daily_digests --date 2025-12-14
```

### Check What Would Be Sent:
```bash
python check_todays_schedule.py
```

## 📞 Support

If you need help setting up Gmail SMTP:
1. Follow Google's official App Password guide
2. Use the exact settings provided above
3. Test with a simple email first
4. Check Gmail's "Less secure app access" if needed (though App Passwords are preferred)

Once SMTP is configured, students will receive daily digest emails in their Gmail inboxes automatically! 🎉
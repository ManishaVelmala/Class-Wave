# 📧 Email Notifications Setup Guide

## Overview
ClassWave now sends reminder emails to students automatically! This guide will help you configure email sending.

## ✅ What's Already Done
- ✅ Email sending code is implemented
- ✅ Reminders are sent via email when due
- ✅ Daily digests can be emailed
- ✅ Update notifications are emailed

## 🚀 Quick Setup (Gmail)

### Step 1: Get Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click on "Security" in the left sidebar
3. Enable "2-Step Verification" if not already enabled
4. Search for "App passwords" or go to: https://myaccount.google.com/apppasswords
5. Select "Mail" and "Other (Custom name)"
6. Enter "ClassWave" as the name
7. Click "Generate"
8. **Copy the 16-character password** (you'll need this)

### Step 2: Configure Settings

Open `lecturebuzz/settings.py` and update the email configuration:

```python
# Comment out the console backend
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Uncomment and configure SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'  # Replace with your Gmail
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'  # Paste the App Password here
DEFAULT_FROM_EMAIL = 'ClassWave <noreply@classwave.com>'
```

### Step 3: Test Email Sending

Run this command to test:
```bash
python manage.py send_reminders
```

If configured correctly, you'll see:
```
✅ Successfully sent X reminder emails!
```

## 📬 How It Works

### 1. Reminder Creation
When a student registers or a schedule is created:
- Reminders are created in the database
- Set for 30 minutes before each class
- Stored with student email and message

### 2. Email Sending
Run the command to send pending reminders:
```bash
python manage.py send_reminders
```

This will:
- Find all reminders where `reminder_time` has passed
- Send email to each student
- Mark reminders as sent

### 3. Automated Sending (Optional)
For automatic sending, set up a cron job or Celery Beat:

#### Option A: Cron Job (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add this line to check every 5 minutes
*/5 * * * * cd /path/to/project && python manage.py send_reminders
```

#### Option B: Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Every 5 minutes
4. Action: Start a program
5. Program: `python`
6. Arguments: `manage.py send_reminders`
7. Start in: Your project directory

#### Option C: Celery Beat (Advanced)
Already configured in `lecturebuzz/celery.py`

## 📧 Email Types

### 1. Class Reminders
**Subject:** 🔔 Class Reminder - [Subject Name]
**When:** 30 minutes before class
**Content:** Date, time, subject, topic, lecturer

### 2. Daily Digest
**Subject:** 📅 Your Schedule for [Date]
**When:** Student's chosen time (7 AM, 8 AM, etc.)
**Content:** All classes for the day in one email

### 3. Update Notifications
**Subject:** ⚠️ Schedule Update - [Subject Name]
**When:** Immediately when lecturer changes schedule
**Content:** What changed in the schedule

## 🧪 Testing

### Test 1: Send Test Reminder
```bash
python manage.py shell
```
```python
from reminders.tasks import send_pending_reminders
count = send_pending_reminders()
print(f"Sent {count} emails")
```

### Test 2: Check Email in Console (Development)
If using console backend, emails print to terminal:
```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: =?utf-8?b?8J+UlCBDbGFzcyBSZW1pbmRlciAtIERhdGEgU3RydWN0dXJlcw==?=
From: ClassWave <noreply@classwave.com>
To: student@example.com
Date: Mon, 08 Dec 2025 10:30:00 -0000
Message-ID: <...>

Reminder: You have a class scheduled!
...
```

## 🔧 Troubleshooting

### Problem: "SMTPAuthenticationError"
**Solution:** 
- Make sure 2-Step Verification is enabled
- Use App Password, not regular Gmail password
- Check EMAIL_HOST_USER is correct

### Problem: "Connection refused"
**Solution:**
- Check EMAIL_HOST and EMAIL_PORT
- Ensure EMAIL_USE_TLS = True
- Check firewall settings

### Problem: Emails not sending
**Solution:**
- Run: `python manage.py send_reminders`
- Check if reminders exist: `python check_reminders.py`
- Verify reminder_time has passed

### Problem: "No pending reminders"
**Solution:**
- Reminders only send when their time arrives
- Check: `python check_reminders.py`
- Create test reminder with past time

## 📊 Monitoring

### Check Reminder Status
```bash
python check_reminders.py
```

Shows:
- Total reminders
- Sent vs pending
- Students with reminders

### Check Sent Emails
In Django admin:
1. Go to http://127.0.0.1:8000/admin/
2. Click "Reminders"
3. Filter by "is_sent = True"

## 🎯 Best Practices

### For Development:
- Use console backend (emails print to terminal)
- Test with your own email first
- Check spam folder

### For Production:
- Use SMTP backend with real email
- Set up automated sending (cron/Celery)
- Monitor email delivery
- Keep App Password secure
- Use environment variables for credentials

## 🔐 Security

### Protect Email Credentials:
Create `.env` file:
```
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

Update `settings.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
```

Add to `.gitignore`:
```
.env
```

## ✅ Summary

1. **Get Gmail App Password** from Google Account
2. **Configure settings.py** with your email and password
3. **Test with:** `python manage.py send_reminders`
4. **Set up automation** (cron job or Celery)
5. **Monitor** with `check_reminders.py`

Your students will now receive reminder emails automatically! 📧✨

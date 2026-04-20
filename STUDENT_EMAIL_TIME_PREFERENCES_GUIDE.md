# Student Email Time Preferences Guide ⏰

## ✅ How Students Set Their Email Reminder Time

**Yes, students can set their preferred time for receiving daily digest emails in their Gmail inbox!**

## 🎯 Available Time Options

Students can choose from these email delivery times:

### Morning Options:
- **6:00 AM** - Early Morning (for early risers)
- **7:00 AM** - Morning (default)
- **8:00 AM** - Before Classes (last-minute check)

### Evening Options:
- **8:00 PM** - Evening (plan for next day)
- **9:00 PM** - Night (plan for next day)

## 📱 How Students Access Preferences

### Step 1: Login to ClassWave
- Student logs in with their credentials
- Goes to their dashboard

### Step 2: Navigate to Digest Settings
- Click **"Notifications"** in navbar
- Click **"Digest Settings"** button
- Or go directly to: `http://127.0.0.1:8000/reminders/digest-preferences/`

### Step 3: Set Preferences
Students can configure:
- ✅ **Enable/Disable** daily digest emails
- ✅ **Choose time** for email delivery
- ✅ **Save preferences**

## 🖥️ Preferences Page Features

### Settings Available:
```
⚙️ Your Preferences

📧 Enable Daily Digest
   [Toggle Switch] Get one notification with all your classes

🕐 When to receive your digest?
   [Dropdown Menu]
   ├── 6:00 AM - Early Morning
   ├── 7:00 AM - Morning (Default)
   ├── 8:00 AM - Before Classes  
   ├── 8:00 PM - Evening (Next Day)
   └── 9:00 PM - Night (Next Day)

[Save My Preferences Button]
```

### Visual Guide:
```
🌅 Morning        ☀️ Before Classes    🌙 Evening
Start your day    Last minute check    Plan for tomorrow
prepared
```

## 🔄 How It Works Behind the Scenes

### 1. Student Sets Preference:
```python
# Student chooses 7:00 AM
DailyDigestPreference.objects.create(
    student=student,
    digest_time='07:00',
    is_enabled=True
)
```

### 2. System Respects Preference:
```python
# Get student's preference
pref = DailyDigestPreference.objects.get(student=student)
digest_time_str = pref.digest_time  # '07:00'
is_enabled = pref.is_enabled  # True

# Send email at their preferred time
if is_enabled:
    send_mail(
        subject=f'📅 Your Schedule for {date}',
        message=digest_message,
        recipient_list=[student.email],  # Their Gmail
        # Scheduled for their preferred time
    )
```

### 3. Email Delivered to Gmail:
- Email sent at student's chosen time
- Appears in their Gmail inbox
- Professional ClassWave format

## 📊 Current Student Preferences

Let me check what preferences are currently set:

### Example Preferences:
- **vaishnavi**: 8:00 AM (before classes)
- **A.Revathi**: 7:00 AM (morning) 
- **PranayaYadav**: 8:00 PM (evening, next day)
- **B.Anusha**: 9:00 PM (night, next day)

## 🎯 Email Delivery Examples

### Morning Delivery (7:00 AM):
```
📧 Gmail Inbox - 7:00 AM
From: ClassWave <noreply@classwave.com>
Subject: 📅 Your Schedule for Thursday, December 11, 2025
To: phularivaishnavi2004@gmail.com

📅 YOUR SCHEDULE FOR Thursday, December 11, 2025
You have 3 classes today...
```

### Evening Delivery (8:00 PM - Day Before):
```
📧 Gmail Inbox - 8:00 PM (December 10)
From: ClassWave <noreply@classwave.com>  
Subject: 📅 Your Schedule for Thursday, December 11, 2025
To: pranayayadav11@gmail.com

📅 YOUR SCHEDULE FOR Thursday, December 11, 2025
You have 3 classes today...
```

## 🚀 Testing Student Preferences

### Test Commands:
```bash
# Check current preferences
python manage.py shell
>>> from reminders.models import DailyDigestPreference
>>> DailyDigestPreference.objects.all()

# Test digest generation with preferences
python test_daily_digest_emails.py

# Send digests respecting all preferences
python manage.py send_daily_digests
```

## 📋 Student Instructions

### For Students to Set Their Email Time:

1. **Login** to ClassWave
2. **Click "Notifications"** in top menu
3. **Click "Digest Settings"** 
4. **Choose your preferred time**:
   - Morning person? → Choose 6:00 AM or 7:00 AM
   - Want last-minute check? → Choose 8:00 AM
   - Prefer evening planning? → Choose 8:00 PM or 9:00 PM
5. **Click "Save My Preferences"**
6. **Done!** You'll receive emails at your chosen time

### Benefits:
- ✅ **Personalized timing** - Get emails when you want them
- ✅ **Gmail delivery** - Emails appear in your inbox
- ✅ **Easy to change** - Update preferences anytime
- ✅ **Can disable** - Turn off if not needed

## ✅ Summary

**Students CAN set their email reminder time:**

1. ✅ **5 time options** available (6 AM to 9 PM)
2. ✅ **Easy preferences page** with visual interface
3. ✅ **System respects** individual preferences
4. ✅ **Emails delivered** to Gmail at chosen time
5. ✅ **Can enable/disable** as needed

Each student receives their daily digest email in their Gmail inbox at their personally chosen time!
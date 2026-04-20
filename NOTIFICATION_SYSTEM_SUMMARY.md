# 📬 ClassWave Notification System

## Overview
ClassWave uses a **Daily Digest** system instead of individual class reminders. Students get ONE email per day with ALL their classes, reducing notification spam.

## ✅ What Students Receive

### 1. Daily Schedule Digest 📅
**When:** Once per day at student's chosen time (7 AM, 8 AM, 8 PM, etc.)
**Content:** ALL classes for the day in ONE email
**Example:**
```
Subject: 📅 Your Schedule for Monday, December 11, 2025

You have 6 classes today:

1. Data Structures
   📚 Topic: Binary Trees
   ⏰ Time: 9:00 AM - 10:00 AM
   👨‍🏫 Lecturer: Prof. Smith

2. Database Management
   📚 Topic: SQL Queries
   ⏰ Time: 10:00 AM - 11:00 AM
   👨‍🏫 Lecturer: Dr. Johnson

... (4 more classes)
```

### 2. Update Notifications ⚠️
**When:** Immediately when a lecturer changes a schedule
**Content:** What changed in the schedule
**Example:**
```
Subject: ⚠️ Schedule Update - Data Structures

Your schedule has been updated:

Old: Monday, 9:00 AM - 10:00 AM
New: Monday, 10:00 AM - 11:00 AM

Topic: Binary Trees
Lecturer: Prof. Smith
```

## ❌ What Students DON'T Receive

### No Individual Class Reminders
- ❌ No "30 minutes before class" emails
- ❌ No separate notification for each class
- ❌ No notification spam (6 classes = 6 emails)

## 🎯 Benefits

### For Students:
- ✅ **Less Email Spam** - One email instead of 6
- ✅ **Better Overview** - See entire day at once
- ✅ **Customizable Timing** - Choose when to receive digest
- ✅ **Clean Inbox** - No clutter

### For System:
- ✅ **Fewer Emails** - 83% reduction in email volume
- ✅ **Better Performance** - Less processing
- ✅ **Easier Management** - One notification type

## 🔧 How It Works

### Student Registration:
1. Student registers with department and batch
2. Automatically assigned to all matching schedules
3. **No individual reminders created**
4. Daily digest preference created (default: 7 AM)

### Daily Digest Generation:
1. System runs daily (midnight or scheduled time)
2. Checks each student's schedule for tomorrow
3. Creates ONE digest with all classes
4. Sends at student's chosen time

### Email Sending:
```bash
# Manual sending
python manage.py send_reminders

# Automated (cron job every 5 minutes)
*/5 * * * * python manage.py send_reminders
```

## ⚙️ Student Settings

Students can customize their digest:

### Enable/Disable:
- Turn daily digest on/off
- Go to: Digest Settings

### Choose Timing:
- 6:00 AM - Early morning
- 7:00 AM - Morning (default)
- 8:00 AM - Before classes
- 8:00 PM - Evening (next day)
- 9:00 PM - Night (next day)

## 📊 Notification Types

| Type | When | Email | In-App |
|------|------|-------|--------|
| Daily Digest | Daily at chosen time | ✅ | ✅ |
| Update Notification | When schedule changes | ✅ | ✅ |
| ~~Class Reminder~~ | ~~30 min before~~ | ❌ | ❌ |

## 🧪 Testing

### Test Daily Digest:
1. Login as student
2. Go to Digest Settings
3. Click "Test - Generate Today's Digest"
4. Check Notifications page

### Test Email Sending:
```bash
# Configure email in settings.py first
python manage.py send_reminders
```

## 📈 Statistics

### Email Reduction:
- **Before:** 6 classes = 6 emails per student
- **After:** 6 classes = 1 email per student
- **Savings:** 83% fewer emails

### Example:
- 100 students with 6 classes each
- **Old system:** 600 emails per day
- **New system:** 100 emails per day
- **Reduction:** 500 fewer emails!

## 🎓 User Experience

### Morning Routine:
1. Student wakes up at 7 AM
2. Receives ONE email with entire day's schedule
3. Reviews all 6 classes at once
4. Plans the day accordingly

### No More:
- ❌ Checking phone every 30 minutes
- ❌ Multiple notification interruptions
- ❌ Cluttered email inbox
- ❌ Missed notifications in spam

## 🔮 Future Enhancements (Optional)

### Possible Additions:
- SMS notifications for digest
- Push notifications (mobile app)
- Weekly digest (all classes for the week)
- Custom reminder times per student
- Digest preview before sending

## ✅ Summary

ClassWave uses a **smart daily digest system**:
- 📅 ONE email per day with ALL classes
- ⚠️ Immediate updates when schedules change
- ❌ NO individual class reminders
- 🎯 83% fewer emails
- ✨ Better user experience

Students stay informed without notification overload!

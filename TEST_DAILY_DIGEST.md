# Test Daily Digest Feature

## 🧪 Quick Test (5 Minutes)

### Step 1: Login as Student
```
http://127.0.0.1:8000/login/
Username: student1
Password: password123
```

### Step 2: Go to Daily Digest Settings
- Click "📅 Daily Digest Settings" button on dashboard
- Or go to: http://127.0.0.1:8000/reminders/digest-preferences/

### Step 3: Configure Preferences
- **Enable**: Make sure it's ON (checked)
- **Time**: Choose "7:00 AM - Morning"
- Click "💾 Save Preferences"

### Step 4: Generate Test Digest
- Click "🧪 Test - Generate Today's Digest" button
- This will create a digest for TODAY (not tomorrow)

### Step 5: View the Digest
- You'll be redirected to Notifications
- Look for a notification with "📅 DAILY DIGEST" badge
- It will show ALL your classes for today in ONE notification!

### Expected Result:
```
📅 DAILY DIGEST

YOUR SCHEDULE FOR Thursday, November 21, 2025

You have 3 classes today:

1. Data Structures
   📚 Topic: Binary Trees
   ⏰ Time: 09:00 AM - 10:30 AM
   👨‍🏫 Lecturer: John Doe
   📍 Department: Computer Science

2. Web Development
   📚 Topic: Django Framework
   ⏰ Time: 11:00 AM - 12:30 PM
   👨‍🏫 Lecturer: John Doe
   📍 Department: Computer Science

3. Database Management
   📚 Topic: SQL Queries
   ⏰ Time: 02:00 PM - 03:30 PM
   👨‍🏫 Lecturer: John Doe
   📍 Department: Computer Science

💡 Tip: Check your calendar for more details!

Have a great day! 🎓
```

---

## 🎯 What to Check

✅ **Digest Settings Page:**
- Toggle works
- Time dropdown works
- Save button works
- Test button works

✅ **Notification:**
- Shows "📅 DAILY DIGEST" badge
- Shows all classes together
- Formatted nicely
- Shows date in title

✅ **Dashboard:**
- Alert box promoting feature
- Link to settings works

---

## 📊 Compare

### Before (Individual Reminders):
```
Notification 1: Data Structures - 09:00 AM
Notification 2: Web Development - 11:00 AM
Notification 3: Database Management - 02:00 PM
... (3 separate notifications)
```

### After (Daily Digest):
```
Notification 1: YOUR SCHEDULE FOR TODAY
  - Data Structures - 09:00 AM
  - Web Development - 11:00 AM
  - Database Management - 02:00 PM
  (ALL in ONE notification!)
```

---

## 🔧 Admin Panel Check

1. Go to: http://127.0.0.1:8000/admin/
2. Login with superuser
3. Check:
   - **Reminders** → See daily_digest type
   - **Daily Digest Preferences** → See student preferences

---

## ✅ Success Criteria

- ✅ Settings page loads
- ✅ Can enable/disable digest
- ✅ Can choose time
- ✅ Test button generates digest
- ✅ Digest shows in notifications
- ✅ All classes shown together
- ✅ Formatted correctly

---

**If all checks pass, the feature is working perfectly!** 🎉

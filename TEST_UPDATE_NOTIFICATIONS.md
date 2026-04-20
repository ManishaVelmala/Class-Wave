# Testing Update Notifications Feature

## Quick Test Guide

### Step 1: Start the Server
```bash
python manage.py runserver
```

### Step 2: Login as Student
1. Go to http://127.0.0.1:8000/login/
2. Username: `student1`
3. Password: `password123`
4. Note: You should see 3 schedules on your dashboard
5. Check the navbar - notification badge should show "0" or be hidden
6. **Keep this browser tab open**

### Step 3: Login as Lecturer (New Tab/Window)
1. Open a new browser tab/window (or use incognito mode)
2. Go to http://127.0.0.1:8000/login/
3. Username: `lecturer1`
4. Password: `password123`
5. You should see your lecturer dashboard with 3 schedules

### Step 4: Edit a Schedule
1. Click "Edit" on any schedule (e.g., "Data Structures")
2. Make a change:
   - Change the date to tomorrow
   - Or change the start time
   - Or change the topic
3. Click "Save Schedule"
4. You should see "Schedule updated successfully!"

### Step 5: Check Student Notifications
1. Go back to the student browser tab
2. Wait a few seconds (or refresh the page)
3. **You should see:**
   - Red notification badge with "1"
   - Badge appears in the navbar next to "🔔 Notifications"

### Step 6: View the Notification
1. Click "🔔 Notifications" in the navbar
2. You should see:
   - A notification with "⚠️ UPDATE" badge
   - "NEW" badge (yellow)
   - The schedule details
   - **A list of changes made** (e.g., "Date: Nov 25 → Nov 26")
   - "Mark as Read" button

### Step 7: Mark as Read
1. Click "Mark as Read"
2. The notification should now show "✓ Read" badge
3. The "NEW" badge should disappear
4. Go back to dashboard
5. The notification badge in navbar should be gone

### Step 8: Test Multiple Updates
1. Go back to lecturer tab
2. Edit another schedule
3. Make different changes (time, topic, etc.)
4. Save it
5. Go to student tab
6. Badge should show "1" again
7. Click notifications to see the new update

### Step 9: Test "Mark All as Read"
1. As lecturer, edit 2-3 more schedules
2. As student, check notifications
3. You should see multiple unread notifications
4. Click "Mark All as Read" button
5. All notifications should be marked as read
6. Badge should disappear

## Expected Results

✅ **Notification Badge:**
- Shows unread count
- Updates automatically
- Disappears when all read

✅ **Update Notifications:**
- Created immediately when schedule is edited
- Shows exactly what changed
- Includes all schedule details
- Marked with "⚠️ UPDATE" badge

✅ **Notification Center:**
- Lists all notifications (updates + reminders)
- Shows read/unread status
- Allows marking individual or all as read
- Displays creation and sent times

✅ **Change Tracking:**
- Shows old value → new value
- Tracks: subject, topic, date, start_time, end_time
- Clear, readable format

## Troubleshooting

### Badge not showing?
- Refresh the page
- Check browser console for errors
- Make sure you're logged in as a student

### Notification not created?
- Check if the schedule actually changed
- Only these fields trigger notifications: subject, topic, date, start_time, end_time
- Check Django admin: http://127.0.0.1:8000/admin/reminders/reminder/

### Changes not showing?
- Make sure you saved the schedule
- Check the notification message - it should list all changes
- Verify in admin panel

## Advanced Testing

### Test with Multiple Students
1. Login as student1, student2, student3 in different browsers
2. Edit a schedule as lecturer
3. All 3 students should get the notification
4. Each can mark as read independently

### Test Different Change Types
- **Date change**: "Date: Nov 25 → Nov 26"
- **Time change**: "Start Time: 09:00 → 10:00"
- **Subject change**: "Subject: Math → Advanced Math"
- **Topic change**: "Topic: Algebra → Calculus"
- **Multiple changes**: All changes listed

### Test Notification Types
- Scheduled reminders: 🔔 REMINDER badge
- Update notifications: ⚠️ UPDATE badge
- Both should appear in the same notification center

## Database Verification

Check in Django Admin:
```
http://127.0.0.1:8000/admin/reminders/reminder/
```

You should see:
- Reminder type: "Update Notification"
- Is sent: False (or True if Celery is running)
- Is read: False (until student marks it)
- Message: Contains the change details

## Console Output

When a schedule is updated, you should see in the Django console:
```
📧 UPDATE NOTIFICATION to student1@example.com:

    ⚠️ SCHEDULE UPDATE ALERT ⚠️
    
    A schedule you're enrolled in has been updated!
    ...
```

## Success Criteria

✅ Notification created when schedule edited
✅ All enrolled students receive notification
✅ Badge shows correct unread count
✅ Changes are clearly listed
✅ Mark as read works
✅ Mark all as read works
✅ Badge updates automatically
✅ Notification center displays correctly

---

**If all tests pass, the feature is working perfectly!** 🎉

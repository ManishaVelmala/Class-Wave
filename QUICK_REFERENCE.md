# LectureBuzz - Quick Reference Card

## 🚀 Getting Started

```bash
# Start the server
python manage.py runserver

# Access the app
http://127.0.0.1:8000/
```

## 👤 Test Accounts

| Role | Username | Password |
|------|----------|----------|
| Lecturer | lecturer1 | password123 |
| Student | student1 | password123 |
| Student | student2 | password123 |
| Student | student3 | password123 |

## 📱 Main Features

### For Students:
- ✅ View schedules (list/calendar)
- ✅ Set reminder times
- ✅ **View notifications** 🆕
- ✅ **Get update alerts** 🆕
- ✅ Edit profile

### For Lecturers:
- ✅ Create schedules
- ✅ Edit schedules (auto-notifies students) 🆕
- ✅ Delete schedules
- ✅ Assign to students/batches
- ✅ View calendar

## 🔗 Important URLs

| Page | URL |
|------|-----|
| Home | `/` |
| Login | `/login/` |
| Student Dashboard | `/schedules/student/` |
| Lecturer Dashboard | `/schedules/lecturer/` |
| Calendar | `/schedules/calendar/` |
| **Notifications** 🆕 | `/reminders/notifications/` |
| Profile | `/profile/` |
| Admin | `/admin/` |

## 🔔 Notification System 🆕

### Notification Types:
- **🔔 REMINDER**: Scheduled before class
- **⚠️ UPDATE**: When schedule changes

### How to View:
1. Click "🔔 Notifications" in navbar
2. Or check the red badge (shows unread count)

### What Triggers Updates:
- Subject name change
- Topic change
- Date change
- Time change

### Mark as Read:
- Individual: Click "Mark as Read"
- All: Click "Mark All as Read"

## 🎯 Common Tasks

### Create a Schedule (Lecturer):
1. Dashboard → "Create New Schedule"
2. Fill in details
3. Select students or batch
4. Save

### Set a Reminder (Student):
1. View schedule
2. Click "Set Reminder"
3. Choose time (10min, 30min, 1hr, etc.)
4. Save

### Check Notifications (Student): 🆕
1. Look for red badge in navbar
2. Click "🔔 Notifications"
3. View updates and reminders
4. Mark as read

### Edit a Schedule (Lecturer):
1. Dashboard → Click "Edit"
2. Make changes
3. Save
4. **Students auto-notified!** 🆕

## 🔧 Admin Panel

```
URL: http://127.0.0.1:8000/admin/

Create superuser:
python manage.py createsuperuser
```

### What You Can Manage:
- Users (students/lecturers)
- Schedules
- Reminders
- Notifications 🆕
- Profiles

## 📊 Sample Data

```bash
# Create test data
python manage.py create_sample_data
```

Creates:
- 1 lecturer
- 3 students
- 3 schedules

## 🐛 Troubleshooting

### Server won't start?
```bash
# Check for errors
python manage.py check

# Try different port
python manage.py runserver 8001
```

### Notifications not showing? 🆕
- Refresh the page
- Check you're logged in as student
- Verify schedule was actually changed

### Database issues?
```bash
# Reset database
del db.sqlite3
python manage.py migrate
python manage.py create_sample_data
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| README.md | Full documentation |
| QUICKSTART.md | Quick setup guide |
| UPDATE_NOTIFICATIONS_GUIDE.md 🆕 | Notification feature guide |
| TEST_UPDATE_NOTIFICATIONS.md 🆕 | Testing instructions |
| WHATS_NEW.md 🆕 | Release notes |
| FEATURES_CHECKLIST.md | Feature list |
| PROJECT_SUMMARY.md | Project overview |

## 🎓 Tips

### For Students:
- Check notifications regularly
- Set reminder times that work for you
- Mark notifications as read to stay organized
- Use calendar view for weekly planning

### For Lecturers:
- Be mindful when editing - students will be notified
- Use batch assignment for efficiency
- Check calendar to avoid conflicts
- Students appreciate timely updates!

## ⌨️ Keyboard Shortcuts

None currently, but you can add them!

## 🔮 Coming Soon

- Email notifications
- SMS alerts
- Push notifications
- Mobile app
- Attendance tracking

## 📞 Need Help?

1. Check documentation files
2. Review Django console output
3. Check admin panel
4. Run `python manage.py check`

## 🎉 Quick Test

```bash
# 1. Start server
python manage.py runserver

# 2. Login as student (Tab 1)
student1 / password123

# 3. Login as lecturer (Tab 2)
lecturer1 / password123

# 4. Edit schedule (Tab 2)
Change date or time → Save

# 5. Check notifications (Tab 1)
See red badge → Click → View update!
```

---

**Version**: 1.1.0
**Status**: ✅ All features working
**Last Updated**: November 20, 2025

**Happy Learning with LectureBuzz!** 🎓

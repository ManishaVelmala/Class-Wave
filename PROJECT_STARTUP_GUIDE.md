# 🚀 PROJECT STARTUP GUIDE - Email Service Management

## 🔄 **When Opening the Project in Kiro/VSCode**

### **The Issue:**
- When you close Kiro/VSCode, the background email service **STOPS**
- When you reopen the project folder, the service is **NOT running**
- Emails won't be sent until you restart the service

### **The Solution:**

#### **🎯 Method 1: Quick Auto-Start (Recommended)**
```bash
# Run this EVERY TIME you open the project
python auto_start_email_service.py
```

#### **🎯 Method 2: Use the Startup Batch File**
```bash
# Double-click this file when you open the project
START_HERE.bat
```

#### **🎯 Method 3: VSCode Tasks (If using VSCode)**
- Press `Ctrl+Shift+P`
- Type "Tasks: Run Task"
- Select "Auto-Start Email Service"

## 📊 **Service Lifecycle Tracking**

### **Check Service History:**
```bash
python service_lifecycle_tracker.py
```

### **What It Shows:**
- When service started/stopped
- How long it ran
- Recommendations for improvement

## 🔍 **Monitoring Commands**

### **Check Current Status:**
```bash
python email_service_status.py
```

### **Live Dashboard:**
```bash
python email_service_dashboard.py
```

### **Health Check:**
```bash
python simple_service_monitor.py
```

## ⚡ **Quick Reference**

### **When You Open the Project:**
1. **ALWAYS** run: `python auto_start_email_service.py`
2. Or double-click: `START_HERE.bat`
3. Verify service is running with status check

### **When Service Stops Working:**
```bash
# Manual restart
python start_continuous_email_service.py

# Or auto-restart
python auto_start_email_service.py
```

### **Daily Workflow:**
1. **Open project** → Run auto-start script
2. **Work on project** → Service runs in background
3. **Close project** → Service stops automatically
4. **Next day** → Repeat step 1

## 🛡️ **Automatic Solutions**

### **Windows Startup (Permanent Solution):**
- Service starts when Windows boots
- Runs even when project is closed
- Setup: `python setup_automatic_system.py`

### **Service Monitoring:**
- Tracks when service starts/stops
- Provides restart recommendations
- Logs service activity

## 📋 **Troubleshooting**

### **Service Won't Start:**
```bash
# Check what's wrong
python service_lifecycle_tracker.py

# Force restart
python start_continuous_email_service.py
```

### **Emails Not Sending:**
```bash
# Check for overdue emails
python simple_service_monitor.py

# Restart service
python auto_start_email_service.py
```

### **Service Keeps Stopping:**
- Use Windows startup method
- Check system resources
- Review service logs

## 🎯 **Best Practices**

### **Every Time You Open the Project:**
1. ✅ Run `python auto_start_email_service.py`
2. ✅ Check that it says "Service is running"
3. ✅ Verify no overdue emails

### **Before Closing the Project:**
1. ✅ Service will stop automatically (this is normal)
2. ✅ No action needed

### **For Long-Term Use:**
1. ✅ Set up Windows startup for permanent solution
2. ✅ Use monitoring tools to track service health
3. ✅ Run lifecycle tracker weekly

## 📧 **Current Email Schedule**

### **Today's Remaining Emails:**
- **PranayaYadav**: 4:10 PM
- **B.Anusha**: 9:00 PM  
- **A.Revathi**: 11:55 PM

### **Service Requirements:**
- Must be running continuously
- Checks every 30 seconds
- Sends emails within 30 seconds of preference time

---

## 🚨 **IMPORTANT REMINDER**

**EVERY TIME you open this project folder in Kiro/VSCode:**

```bash
python auto_start_email_service.py
```

**This ensures emails are sent at the correct times!**
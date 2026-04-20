# Quick Test: Forgot Password Feature

## 🚀 5-Minute Test Guide

### Step 1: Go to Login Page
```
http://127.0.0.1:8000/login/
```

### Step 2: Click "Forgot Password?"
You'll see the link below the login button.

### Step 3: Enter Email
```
student1@example.com
```
or
```
lecturer1@example.com
```

Click "📧 Send Reset Link"

### Step 4: Check Console
Look at your terminal where the server is running. You'll see something like:

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: LectureBuzz - Password Reset Request
From: webmaster@localhost
To: student1@example.com
Date: ...

Hello student1,

You're receiving this email because you requested a password reset...

http://127.0.0.1:8000/password-reset-confirm/...
```

### Step 5: Copy the Reset Link
Copy the entire link that starts with:
```
http://127.0.0.1:8000/password-reset-confirm/...
```

### Step 6: Open the Link
Paste it in your browser and press Enter.

### Step 7: Set New Password
- Enter new password: `newpassword123`
- Confirm password: `newpassword123`
- Click "✅ Change My Password"

### Step 8: Login
- Click "🔐 Login Now"
- Username: `student1`
- Password: `newpassword123` (your new password)
- Click "Login"

### ✅ Success!
You should now be logged in with your new password!

---

## 📝 Notes

- In development mode, emails are printed to console
- Reset links expire in 24 hours
- Each link can only be used once
- Password must be at least 8 characters

## 🔧 For Production

To send real emails, configure in `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
```

---

**That's it! The forgot password feature is working!** 🎉

# Password Reset Feature Guide

## 🔐 Overview

LectureBuzz now includes a complete "Forgot Password" feature that allows users to reset their passwords securely via email.

## ✨ Features

- ✅ Email-based password reset
- ✅ Secure token generation (expires in 24 hours)
- ✅ User-friendly interface
- ✅ Step-by-step process
- ✅ Email validation
- ✅ Password strength requirements
- ✅ Works for both students and lecturers

## 🔄 Password Reset Flow

```
User clicks "Forgot Password?"
        ↓
Enters email address
        ↓
System sends reset email
        ↓
User clicks link in email
        ↓
User enters new password
        ↓
Password updated successfully
        ↓
User can login with new password
```

## 📱 How to Use

### For Users:

#### Step 1: Access Password Reset
1. Go to login page: http://127.0.0.1:8000/login/
2. Click "Forgot Password?" link

#### Step 2: Enter Email
1. Enter your registered email address
2. Click "📧 Send Reset Link"
3. You'll see a confirmation message

#### Step 3: Check Email
1. Check your email inbox
2. Look for email from LectureBuzz
3. Subject: "LectureBuzz - Password Reset Request"
4. Click the reset link in the email

**Note:** In development mode, the email will be printed to the console where the server is running.

#### Step 4: Set New Password
1. Enter your new password
2. Confirm the password
3. Click "✅ Change My Password"

#### Step 5: Login
1. You'll see a success message
2. Click "🔐 Login Now"
3. Login with your new password

## 🌐 URLs

| Page | URL |
|------|-----|
| Forgot Password | `/password-reset/` |
| Email Sent Confirmation | `/password-reset/done/` |
| Set New Password | `/password-reset-confirm/<token>/` |
| Reset Complete | `/password-reset-complete/` |

## 🧪 Testing the Feature

### Development Mode (Console Email):

1. **Start the server:**
   ```bash
   python manage.py runserver
   ```

2. **Go to login page:**
   ```
   http://127.0.0.1:8000/login/
   ```

3. **Click "Forgot Password?"**

4. **Enter email:**
   - Use: `student1@example.com` or `lecturer1@example.com`
   - Click "Send Reset Link"

5. **Check the console:**
   - Look at the terminal where the server is running
   - You'll see the email content printed
   - Copy the reset link from the console

6. **Open the reset link:**
   - Paste the link in your browser
   - It will look like: `http://127.0.0.1:8000/password-reset-confirm/...`

7. **Set new password:**
   - Enter new password twice
   - Click "Change My Password"

8. **Login:**
   - Use the new password to login

### Production Mode (Real Email):

1. **Configure email settings in `settings.py`:**
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.gmail.com'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'your_email@gmail.com'
   EMAIL_HOST_PASSWORD = 'your_app_password'
   DEFAULT_FROM_EMAIL = 'LectureBuzz <noreply@lecturebuzz.com>'
   ```

2. **For Gmail:**
   - Enable 2-factor authentication
   - Generate an "App Password"
   - Use the app password in EMAIL_HOST_PASSWORD

3. **Test:**
   - Follow the same steps as development mode
   - Email will be sent to the actual email address

## 📧 Email Configuration

### Development (Current Setup):
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
- Emails printed to console
- No email server needed
- Perfect for testing

### Production (Gmail):
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
```

### Production (Other SMTP):
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yourprovider.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@example.com'
EMAIL_HOST_PASSWORD = 'your_password'
```

## 🔒 Security Features

1. **Token Expiration:**
   - Reset links expire after 24 hours
   - Prevents old links from being used

2. **One-Time Use:**
   - Each link can only be used once
   - After password reset, link becomes invalid

3. **Secure Token:**
   - Uses Django's built-in token generator
   - Cryptographically secure

4. **Password Validation:**
   - Minimum 8 characters
   - Not too similar to user info
   - Not a common password
   - Not entirely numeric

5. **Email Verification:**
   - Only registered emails can reset passwords
   - Prevents unauthorized access

## 🎨 User Interface

### Pages Included:

1. **Password Reset Request** (`password_reset.html`)
   - Clean form to enter email
   - Helpful instructions
   - Links to login and registration

2. **Email Sent Confirmation** (`password_reset_done.html`)
   - Success message
   - Instructions on what to do next
   - Note about checking spam folder

3. **Set New Password** (`password_reset_confirm.html`)
   - Form to enter new password
   - Password requirements displayed
   - Confirmation field
   - Error handling for invalid links

4. **Reset Complete** (`password_reset_complete.html`)
   - Success message
   - Direct link to login
   - Encouraging message

## 📝 Email Template

The reset email includes:
- Personalized greeting with username
- Clear reset link
- Expiration notice (24 hours)
- Security note (ignore if not requested)
- Professional signature

## ⚠️ Common Issues & Solutions

### Issue: Email not received
**Solution:**
- In development: Check the console output
- In production: Check spam folder
- Verify email address is correct
- Check email server configuration

### Issue: Link expired
**Solution:**
- Request a new reset link
- Links expire after 24 hours

### Issue: Link already used
**Solution:**
- Request a new reset link
- Each link can only be used once

### Issue: Invalid link error
**Solution:**
- Make sure you copied the entire link
- Request a new reset link
- Check if link has expired

### Issue: Password doesn't meet requirements
**Solution:**
- Use at least 8 characters
- Mix letters and numbers
- Avoid common passwords
- Don't use only numbers

## 🔧 Customization

### Change Link Expiration Time:

In `settings.py`, add:
```python
PASSWORD_RESET_TIMEOUT = 86400  # 24 hours in seconds
# Change to 3600 for 1 hour, 7200 for 2 hours, etc.
```

### Customize Email Template:

Edit `templates/accounts/password_reset_email.html`

### Customize Subject:

Edit `templates/accounts/password_reset_subject.txt`

### Change Email Sender:

In `settings.py`:
```python
DEFAULT_FROM_EMAIL = 'Your Name <noreply@yourdomain.com>'
```

## 📊 Files Added/Modified

### New Files:
- `templates/accounts/password_reset.html`
- `templates/accounts/password_reset_done.html`
- `templates/accounts/password_reset_confirm.html`
- `templates/accounts/password_reset_complete.html`
- `templates/accounts/password_reset_email.html`
- `templates/accounts/password_reset_subject.txt`
- `PASSWORD_RESET_GUIDE.md` (this file)

### Modified Files:
- `accounts/urls.py` - Added password reset URLs
- `templates/accounts/login.html` - Added "Forgot Password?" link
- `lecturebuzz/settings.py` - Added email configuration

## 🎯 Best Practices

1. **For Users:**
   - Use a strong, unique password
   - Don't share reset links
   - Complete the reset process promptly
   - Keep your email secure

2. **For Administrators:**
   - Use secure email provider
   - Enable 2FA on email account
   - Monitor reset requests
   - Keep email credentials secure
   - Use environment variables for sensitive data

3. **For Production:**
   - Use real SMTP server
   - Enable SSL/TLS
   - Use app-specific passwords
   - Set up proper domain
   - Test thoroughly before deployment

## 🚀 Quick Test

```bash
# 1. Start server
python manage.py runserver

# 2. Go to login page
http://127.0.0.1:8000/login/

# 3. Click "Forgot Password?"

# 4. Enter: student1@example.com

# 5. Check console for email

# 6. Copy reset link from console

# 7. Paste in browser

# 8. Set new password

# 9. Login with new password
```

## ✅ Feature Status

- ✅ Password reset request page
- ✅ Email sending functionality
- ✅ Token generation and validation
- ✅ New password form
- ✅ Success confirmation
- ✅ Email templates
- ✅ Security measures
- ✅ User-friendly interface
- ✅ Error handling
- ✅ Documentation

---

**Feature Status**: ✅ COMPLETE & WORKING

**Version**: 1.2.0

**Last Updated**: November 21, 2025

**The password reset feature is production-ready and fully functional!** 🎉

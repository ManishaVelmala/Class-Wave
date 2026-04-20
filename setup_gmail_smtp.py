#!/usr/bin/env python
"""
Interactive setup for Gmail SMTP to send real emails to students
"""

def setup_gmail_smtp():
    print("🔧 GMAIL SMTP SETUP FOR CLASSWAVE")
    print("=" * 50)
    print()
    
    print("📧 To send emails to student Gmail inboxes, we need to configure SMTP.")
    print()
    
    # Get user input
    print("Please provide the following information:")
    print()
    
    gmail_address = input("1. Your Gmail address (to send FROM): ")
    if not gmail_address:
        print("❌ Gmail address is required!")
        return
    
    print()
    print("2. Gmail App Password:")
    print("   - Go to Google Account → Security")
    print("   - Enable 2-Factor Authentication")
    print("   - Create App Password for 'Mail'")
    print("   - Copy the 16-character password")
    print()
    
    app_password = input("   Enter App Password (16 characters): ")
    if not app_password:
        print("❌ App password is required!")
        return
    
    # Generate settings
    settings_content = f'''
# Email Configuration - REAL GMAIL DELIVERY
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '{gmail_address}'
EMAIL_HOST_PASSWORD = '{app_password}'
DEFAULT_FROM_EMAIL = 'ClassWave <{gmail_address}>'

# Alternative backends (comment out when using SMTP):
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Testing only
# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'  # Save to files
'''
    
    print()
    print("📝 GENERATED SETTINGS:")
    print("-" * 30)
    print(settings_content)
    
    print()
    print("🔧 NEXT STEPS:")
    print("1. Copy the settings above")
    print("2. Replace the email section in lecturebuzz/settings.py")
    print("3. Run: python manage.py send_real_daily_digests --force")
    print("4. Check student Gmail inboxes!")
    
    print()
    confirm = input("Would you like me to create a settings file? (y/n): ")
    
    if confirm.lower() == 'y':
        with open('gmail_settings.txt', 'w') as f:
            f.write(settings_content)
        print("✅ Settings saved to 'gmail_settings.txt'")
        print("📋 Copy this content to your settings.py file")
    
    return gmail_address, app_password

if __name__ == "__main__":
    setup_gmail_smtp()
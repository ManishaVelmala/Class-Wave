#!/usr/bin/env python
"""
Helper script to update Gmail app password in settings.py
"""

def fix_gmail_auth():
    print("🔧 GMAIL AUTHENTICATION FIX")
    print("=" * 50)
    
    print("📋 STEPS TO FIX:")
    print("1. Go to: https://myaccount.google.com/security")
    print("2. Click: App passwords")
    print("3. Delete old 'ClassWave' app password")
    print("4. Create NEW app password for 'ClassWave'")
    print("5. Copy the 16-character password (e.g., 'abcd efgh ijkl mnop')")
    print()
    
    new_password = input("📝 Enter the NEW app password: ").strip()
    
    if len(new_password) == 0:
        print("❌ No password entered")
        return
    
    # Remove spaces if present
    clean_password = new_password.replace(' ', '')
    
    print(f"\n🔄 Updating settings.py...")
    
    # Read current settings
    with open('lecturebuzz/settings.py', 'r') as f:
        content = f.read()
    
    # Replace the password
    old_line = "EMAIL_HOST_PASSWORD = 'owilptgyfmtmyqvi'"
    new_line = f"EMAIL_HOST_PASSWORD = '{clean_password}'"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        
        # Write back
        with open('lecturebuzz/settings.py', 'w') as f:
            f.write(content)
        
        print(f"✅ Updated EMAIL_HOST_PASSWORD in settings.py")
        print(f"🧪 Test with: python quick_gmail_test.py")
    else:
        print(f"❌ Could not find password line in settings.py")
        print(f"💡 Manually update: EMAIL_HOST_PASSWORD = '{clean_password}'")

if __name__ == "__main__":
    fix_gmail_auth()
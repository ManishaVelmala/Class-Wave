#!/usr/bin/env python
"""
Step-by-step Gmail authentication setup guide
"""

import webbrowser
import time

def gmail_setup_guide():
    print("🔧 GMAIL AUTHENTICATION SETUP GUIDE")
    print("=" * 60)
    
    print("📋 STEP-BY-STEP INSTRUCTIONS:")
    print()
    
    print("1️⃣ OPEN GOOGLE ACCOUNT SECURITY:")
    print("   Opening: https://myaccount.google.com/security")
    
    try:
        webbrowser.open("https://myaccount.google.com/security")
        print("   ✅ Browser opened")
    except:
        print("   💡 Manually go to: https://myaccount.google.com/security")
    
    input("\n   Press ENTER when you're on the Google Account Security page...")
    
    print("\n2️⃣ ENABLE 2-STEP VERIFICATION (if not already enabled):")
    print("   - Look for '2-Step Verification'")
    print("   - If it says 'Off', click it and turn it ON")
    print("   - Follow the setup process")
    
    input("   Press ENTER when 2-Step Verification is enabled...")
    
    print("\n3️⃣ CREATE APP PASSWORD:")
    print("   - Look for 'App passwords' section")
    print("   - Click 'App passwords'")
    print("   - You might need to enter your Google password")
    
    input("   Press ENTER when you're on the App passwords page...")
    
    print("\n4️⃣ DELETE OLD PASSWORD (if exists):")
    print("   - Look for any existing 'ClassWave' or similar app password")
    print("   - Click the trash/delete icon to remove it")
    
    input("   Press ENTER when old passwords are deleted...")
    
    print("\n5️⃣ CREATE NEW APP PASSWORD:")
    print("   - Click 'Select app' → Choose 'Other (Custom name)'")
    print("   - Type: ClassWave")
    print("   - Click 'Generate'")
    
    input("   Press ENTER when you see the 16-character password...")
    
    print("\n6️⃣ COPY THE PASSWORD:")
    print("   - You'll see something like: 'abcd efgh ijkl mnop'")
    print("   - Copy this EXACTLY (with or without spaces)")
    
    new_password = input("   📝 Paste the new app password here: ").strip()
    
    if len(new_password) == 0:
        print("   ❌ No password entered. Please run this script again.")
        return
    
    # Clean the password (remove spaces)
    clean_password = new_password.replace(' ', '')
    
    if len(clean_password) != 16:
        print(f"   ⚠️ Warning: Password length is {len(clean_password)}, expected 16")
        print("   💡 Make sure you copied the complete password")
    
    print(f"\n7️⃣ UPDATING SETTINGS.PY:")
    print(f"   New password: {clean_password}")
    
    # Update settings.py
    try:
        with open('lecturebuzz/settings.py', 'r') as f:
            content = f.read()
        
        # Find and replace the password line
        import re
        pattern = r"EMAIL_HOST_PASSWORD = '[^']*'"
        new_line = f"EMAIL_HOST_PASSWORD = '{clean_password}'"
        
        if re.search(pattern, content):
            content = re.sub(pattern, new_line, content)
            
            with open('lecturebuzz/settings.py', 'w') as f:
                f.write(content)
            
            print("   ✅ Updated EMAIL_HOST_PASSWORD in settings.py")
        else:
            print("   ❌ Could not find EMAIL_HOST_PASSWORD line")
            print(f"   💡 Manually update: EMAIL_HOST_PASSWORD = '{clean_password}'")
    
    except Exception as e:
        print(f"   ❌ Error updating settings: {e}")
        print(f"   💡 Manually update: EMAIL_HOST_PASSWORD = '{clean_password}'")
    
    print(f"\n8️⃣ TESTING CONNECTION:")
    print("   Running Gmail connection test...")
    
    return clean_password

if __name__ == "__main__":
    password = gmail_setup_guide()
    if password:
        print(f"\n🧪 Now testing with: python quick_gmail_test.py")
        import subprocess
        try:
            result = subprocess.run(['python', 'quick_gmail_test.py'], 
                                  capture_output=True, text=True, timeout=30)
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
        except Exception as e:
            print(f"Test failed: {e}")
            print("💡 Run manually: python quick_gmail_test.py")
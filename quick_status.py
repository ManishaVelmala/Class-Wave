#!/usr/bin/env python3
"""
Quick Status - Fast check if email service is running
"""

import subprocess
import sys
import os

def quick_service_check():
    """Quick check if service is running"""
    
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        
        if 'python.exe' in result.stdout:
            print("✅ EMAIL SERVICE: RUNNING")
            return True
        else:
            print("❌ EMAIL SERVICE: STOPPED")
            print("💡 Run: python auto_start_email_service.py")
            return False
            
    except:
        print("⚠️  EMAIL SERVICE: UNKNOWN")
        print("💡 Run: python auto_start_email_service.py")
        return False

if __name__ == "__main__":
    quick_service_check()
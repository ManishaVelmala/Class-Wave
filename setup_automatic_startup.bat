@echo off
echo 🚀 SETTING UP AUTOMATIC EMAIL SERVICE
echo =====================================
echo.
echo This will make the email service start automatically when Windows starts
echo.

REM Get current directory
set CURRENT_DIR=%cd%
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

echo 📍 Current directory: %CURRENT_DIR%
echo 📁 Startup folder: %STARTUP_FOLDER%
echo.

REM Create startup batch file
echo 🔧 Creating startup script...
(
echo @echo off
echo cd /d "%CURRENT_DIR%"
echo echo Starting ClassWave Email Service...
echo python start_continuous_email_service.py
) > "%STARTUP_FOLDER%\ClassWave_Email_Service.bat"

if exist "%STARTUP_FOLDER%\ClassWave_Email_Service.bat" (
    echo ✅ Startup script created successfully!
    echo.
    echo 📋 WHAT WAS CREATED:
    echo    File: %STARTUP_FOLDER%\ClassWave_Email_Service.bat
    echo    Purpose: Starts email service when Windows boots
    echo.
    echo 🎯 WHAT HAPPENS NOW:
    echo    ✅ Email service will start automatically when you restart Windows
    echo    ✅ Service runs in background continuously
    echo    ✅ Emails sent at exact preference times
    echo.
    echo 📧 TODAY'S REMAINING EMAILS:
    echo    • PranayaYadav: 4:10 PM
    echo    • B.Anusha: 9:00 PM  
    echo    • A.Revathi: 11:55 PM
    echo.
    echo 💡 TO START NOW WITHOUT REBOOT:
    echo    Run: python start_continuous_email_service.py
    echo.
    echo 🎉 AUTOMATIC STARTUP SETUP COMPLETE!
) else (
    echo ❌ Error: Could not create startup script
    echo 💡 Try running as Administrator
)

pause
#!/usr/bin/env python3
"""
Service Lifecycle Tracker - Track when the email service starts and stops
Logs service activity and provides restart recommendations
"""

import os
import sys
import django
import time
import json
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lecturebuzz.settings')
sys.path.append('.')
django.setup()

LOG_FILE = 'email_service_log.json'

def load_service_log():
    """Load the service activity log"""
    
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {'events': [], 'last_check': None}
    else:
        return {'events': [], 'last_check': None}

def save_service_log(log_data):
    """Save the service activity log"""
    
    try:
        with open(LOG_FILE, 'w') as f:
            json.dump(log_data, f, indent=2, default=str)
    except Exception as e:
        print(f"Warning: Could not save log: {e}")

def log_service_event(event_type, details=None):
    """Log a service event"""
    
    log_data = load_service_log()
    
    event = {
        'timestamp': datetime.now().isoformat(),
        'type': event_type,
        'details': details or {}
    }
    
    log_data['events'].append(event)
    log_data['last_check'] = datetime.now().isoformat()
    
    # Keep only last 50 events
    if len(log_data['events']) > 50:
        log_data['events'] = log_data['events'][-50:]
    
    save_service_log(log_data)

def check_service_running():
    """Check if service is currently running"""
    
    try:
        import subprocess
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        
        # Simple check - if Python is running, assume service might be too
        return 'python.exe' in result.stdout
        
    except:
        return False

def analyze_service_patterns():
    """Analyze service start/stop patterns"""
    
    log_data = load_service_log()
    events = log_data['events']
    
    if not events:
        return {
            'total_starts': 0,
            'total_stops': 0,
            'average_uptime': 0,
            'last_start': None,
            'last_stop': None,
            'recommendations': ['No service history found']
        }
    
    starts = [e for e in events if e['type'] == 'service_started']
    stops = [e for e in events if e['type'] == 'service_stopped']
    checks = [e for e in events if e['type'] == 'service_check']
    
    # Calculate uptime periods
    uptimes = []
    for i, start in enumerate(starts):
        start_time = datetime.fromisoformat(start['timestamp'])
        
        # Find next stop after this start
        next_stop = None
        for stop in stops:
            stop_time = datetime.fromisoformat(stop['timestamp'])
            if stop_time > start_time:
                next_stop = stop_time
                break
        
        if next_stop:
            uptime = (next_stop - start_time).total_seconds() / 3600  # hours
            uptimes.append(uptime)
    
    avg_uptime = sum(uptimes) / len(uptimes) if uptimes else 0
    
    # Generate recommendations
    recommendations = []
    
    if len(starts) > len(stops):
        recommendations.append("Service may still be running")
    elif len(stops) > len(starts):
        recommendations.append("Service stopped more than started - check for issues")
    
    if avg_uptime < 1:
        recommendations.append("Service uptime is low - consider using Windows startup")
    elif avg_uptime > 8:
        recommendations.append("Good service uptime - system is stable")
    
    recent_events = events[-5:] if len(events) >= 5 else events
    recent_stops = [e for e in recent_events if e['type'] == 'service_stopped']
    
    if len(recent_stops) > 2:
        recommendations.append("Frequent stops detected - service may need attention")
    
    return {
        'total_starts': len(starts),
        'total_stops': len(stops),
        'average_uptime': avg_uptime,
        'last_start': starts[-1]['timestamp'] if starts else None,
        'last_stop': stops[-1]['timestamp'] if stops else None,
        'recommendations': recommendations or ['Service appears stable']
    }

def track_service_lifecycle():
    """Track the service lifecycle"""
    
    print("📊 SERVICE LIFECYCLE TRACKER")
    print("=" * 30)
    
    current_time = datetime.now()
    print(f"Check time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if service is running
    service_running = check_service_running()
    
    # Load previous state
    log_data = load_service_log()
    last_check = log_data.get('last_check')
    
    if last_check:
        last_check_time = datetime.fromisoformat(last_check)
        time_since_check = (current_time - last_check_time).total_seconds()
        
        # If it's been more than 10 minutes since last check, assume service might have stopped
        if time_since_check > 600:  # 10 minutes
            if service_running:
                log_service_event('service_started', {
                    'reason': 'detected_after_gap',
                    'gap_minutes': time_since_check / 60
                })
                print(f"✅ Service detected running (after {time_since_check/60:.1f}min gap)")
            else:
                log_service_event('service_stopped', {
                    'reason': 'detected_stopped',
                    'gap_minutes': time_since_check / 60
                })
                print(f"❌ Service detected stopped (after {time_since_check/60:.1f}min gap)")
    else:
        # First time checking
        if service_running:
            log_service_event('service_started', {'reason': 'first_check'})
            print("✅ Service detected running (first check)")
        else:
            log_service_event('service_stopped', {'reason': 'first_check'})
            print("❌ Service not running (first check)")
    
    # Log this check
    log_service_event('service_check', {
        'service_running': service_running,
        'project_opened': True
    })
    
    # Analyze patterns
    analysis = analyze_service_patterns()
    
    print(f"\n📈 SERVICE STATISTICS:")
    print(f"   Total starts: {analysis['total_starts']}")
    print(f"   Total stops: {analysis['total_stops']}")
    print(f"   Average uptime: {analysis['average_uptime']:.1f} hours")
    
    if analysis['last_start']:
        last_start = datetime.fromisoformat(analysis['last_start'])
        print(f"   Last started: {last_start.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if analysis['last_stop']:
        last_stop = datetime.fromisoformat(analysis['last_stop'])
        print(f"   Last stopped: {last_stop.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in analysis['recommendations']:
        print(f"   • {rec}")
    
    return service_running, analysis

def show_service_history():
    """Show recent service history"""
    
    log_data = load_service_log()
    events = log_data['events']
    
    if not events:
        print("No service history found")
        return
    
    print(f"\n📋 RECENT SERVICE HISTORY:")
    print("=" * 28)
    
    # Show last 10 events
    recent_events = events[-10:] if len(events) >= 10 else events
    
    for event in recent_events:
        timestamp = datetime.fromisoformat(event['timestamp'])
        event_type = event['type'].replace('_', ' ').title()
        
        print(f"   {timestamp.strftime('%m-%d %H:%M')} | {event_type}")
        
        if event.get('details'):
            details = event['details']
            if 'reason' in details:
                print(f"                    Reason: {details['reason']}")

def main():
    """Main function"""
    
    print("🔍 EMAIL SERVICE LIFECYCLE TRACKING")
    print("=" * 37)
    
    # Track current lifecycle
    service_running, analysis = track_service_lifecycle()
    
    # Show history
    show_service_history()
    
    # Provide action recommendations
    print(f"\n🎯 CURRENT STATUS:")
    if service_running:
        print("   ✅ Service appears to be running")
        print("   💡 No action needed")
    else:
        print("   ❌ Service is not running")
        print("   🚀 Run: python auto_start_email_service.py")
    
    print(f"\n📝 TRACKING INFO:")
    print(f"   • Service activity is logged to: {LOG_FILE}")
    print(f"   • Run this script to track service lifecycle")
    print(f"   • Helps identify when service stops/starts")

if __name__ == "__main__":
    main()
"""
Alarm management system
"""
from datetime import datetime, timedelta
import json
import os
from threading import Lock
from config import SNOOZE_DURATION_MINUTES, MAX_ALARMS

ALARMS_FILE = 'alarms.json'


class Alarm:
    def __init__(self, alarm_id, time_str, days=None, enabled=True, label=""):
        self.id = alarm_id
        self.time_str = time_str  # Format: "HH:MM"
        self.days = days if days else []  # List of weekday numbers (0=Monday, 6=Sunday)
        self.enabled = enabled
        self.label = label
        self.snooze_until = None
        self.last_triggered = None
    
    def to_dict(self):
        """Convert alarm to dictionary"""
        return {
            'id': self.id,
            'time': self.time_str,
            'days': self.days,
            'enabled': self.enabled,
            'label': self.label,
            'snooze_until': self.snooze_until.isoformat() if self.snooze_until else None,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create alarm from dictionary"""
        alarm = cls(
            data['id'],
            data['time'],
            data.get('days', []),
            data.get('enabled', True),
            data.get('label', '')
        )
        if data.get('snooze_until'):
            alarm.snooze_until = datetime.fromisoformat(data['snooze_until'])
        if data.get('last_triggered'):
            alarm.last_triggered = datetime.fromisoformat(data['last_triggered'])
        return alarm
    
    def should_trigger(self, current_time=None):
        """Check if alarm should trigger now"""
        if not self.enabled:
            return False
        
        if current_time is None:
            current_time = datetime.now()
        
        # Check if snoozed
        if self.snooze_until and current_time < self.snooze_until:
            return False
        
        # Parse alarm time
        hour, minute = map(int, self.time_str.split(':'))
        alarm_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Check if it's the right day
        if self.days:
            weekday = current_time.weekday()  # 0=Monday, 6=Sunday
            if weekday not in self.days:
                return False
        
        # Check if time matches (within 1 minute window)
        time_diff = abs((current_time - alarm_time).total_seconds())
        if time_diff <= 60:  # 1 minute window
            # Check if we already triggered this alarm today
            if self.last_triggered:
                if self.last_triggered.date() == current_time.date():
                    return False
            return True
        
        return False
    
    def snooze(self, minutes=SNOOZE_DURATION_MINUTES):
        """Snooze the alarm"""
        self.snooze_until = datetime.now() + timedelta(minutes=minutes)
    
    def dismiss(self):
        """Dismiss the alarm"""
        self.last_triggered = datetime.now()
        self.snooze_until = None


class AlarmManager:
    def __init__(self):
        self.alarms = []
        self.lock = Lock()
        self.next_id = 1
        self.load_alarms()
    
    def load_alarms(self):
        """Load alarms from file"""
        if os.path.exists(ALARMS_FILE):
            try:
                with open(ALARMS_FILE, 'r') as f:
                    data = json.load(f)
                    self.alarms = [Alarm.from_dict(a) for a in data.get('alarms', [])]
                    self.next_id = data.get('next_id', 1)
            except Exception as e:
                print(f"Error loading alarms: {e}")
                self.alarms = []
                self.next_id = 1
    
    def save_alarms(self):
        """Save alarms to file"""
        try:
            with self.lock:
                data = {
                    'alarms': [a.to_dict() for a in self.alarms],
                    'next_id': self.next_id
                }
                with open(ALARMS_FILE, 'w') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving alarms: {e}")
    
    def add_alarm(self, time_str, days=None, enabled=True, label=""):
        """Add a new alarm"""
        if len(self.alarms) >= MAX_ALARMS:
            raise ValueError(f"Maximum number of alarms ({MAX_ALARMS}) reached")
        
        alarm = Alarm(self.next_id, time_str, days, enabled, label)
        self.next_id += 1
        self.alarms.append(alarm)
        self.save_alarms()
        return alarm
    
    def get_alarm(self, alarm_id):
        """Get alarm by ID"""
        for alarm in self.alarms:
            if alarm.id == alarm_id:
                return alarm
        return None
    
    def update_alarm(self, alarm_id, time_str=None, days=None, enabled=None, label=None):
        """Update an existing alarm"""
        alarm = self.get_alarm(alarm_id)
        if not alarm:
            return None
        
        if time_str is not None:
            alarm.time_str = time_str
        if days is not None:
            alarm.days = days
        if enabled is not None:
            alarm.enabled = enabled
        if label is not None:
            alarm.label = label
        
        self.save_alarms()
        return alarm
    
    def delete_alarm(self, alarm_id):
        """Delete an alarm"""
        alarm = self.get_alarm(alarm_id)
        if alarm:
            self.alarms.remove(alarm)
            self.save_alarms()
            return True
        return False
    
    def get_all_alarms(self):
        """Get all alarms"""
        return self.alarms.copy()
    
    def check_alarms(self, current_time=None):
        """Check which alarms should trigger"""
        if current_time is None:
            current_time = datetime.now()
        
        triggered = []
        for alarm in self.alarms:
            if alarm.should_trigger(current_time):
                triggered.append(alarm)
        
        return triggered
    
    def snooze_alarm(self, alarm_id, minutes=SNOOZE_DURATION_MINUTES):
        """Snooze an alarm"""
        alarm = self.get_alarm(alarm_id)
        if alarm:
            alarm.snooze(minutes)
            self.save_alarms()
            return True
        return False
    
    def dismiss_alarm(self, alarm_id):
        """Dismiss an alarm"""
        alarm = self.get_alarm(alarm_id)
        if alarm:
            alarm.dismiss()
            self.save_alarms()
            return True
        return False


"""
Database-based alarm management system
"""
from datetime import datetime, timedelta
import json
from database import get_db


class DBAlarm:
    def __init__(self, row):
        self.id = row['id']
        self.user_id = row.get('user_id')
        self.time_str = row['time']
        self.days = json.loads(row['days']) if row.get('days') else []
        self.enabled = bool(row['enabled'])
        self.label = row.get('label') or ''
        self.sound_file = row.get('sound_file')
        self.snooze_allowed = bool(row.get('snooze_allowed', 1))
        self.snooze_duration = row.get('snooze_duration', 5)
        self.snooze_until = datetime.fromisoformat(row['snooze_until']) if row.get('snooze_until') else None
        self.last_triggered = datetime.fromisoformat(row['last_triggered']) if row.get('last_triggered') else None
    
    def to_dict(self):
        """Convert alarm to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'time': self.time_str,
            'days': self.days,
            'enabled': self.enabled,
            'label': self.label,
            'sound_file': self.sound_file,
            'snooze_allowed': self.snooze_allowed,
            'snooze_duration': self.snooze_duration,
            'snooze_until': self.snooze_until.isoformat() if self.snooze_until else None,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None
        }
    
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


class DBAlarmManager:
    def __init__(self):
        from database import init_database
        init_database()
    
    def add_alarm(self, user_id, time_str, days=None, enabled=True, label="", 
                  sound_file=None, snooze_allowed=True, snooze_duration=5):
        """Add a new alarm"""
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Konvertiere days zu JSON-String
            if days is None:
                days_json = None
            elif isinstance(days, list):
                days_json = json.dumps(days) if days else None
            else:
                # Falls days kein List ist, versuche es zu konvertieren
                days_json = json.dumps(list(days)) if days else None
            
            # Debug-Logging
            print(f"DB: Adding alarm - user_id={user_id}, time={time_str}, days_json={days_json}")
            
            cursor.execute('''
                INSERT INTO alarms (user_id, time, days, enabled, label, sound_file, 
                                  snooze_allowed, snooze_duration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, time_str, days_json, enabled, label, sound_file, 
                  snooze_allowed, snooze_duration))
            
            alarm_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            result = self.get_alarm(alarm_id)
            if not result:
                print(f"Error: Alarm {alarm_id} was created but could not be retrieved")
            return result
        except Exception as e:
            print(f"Error in add_alarm: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_alarm(self, alarm_id):
        """Get alarm by ID"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM alarms WHERE id = ?', (alarm_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return DBAlarm(row)
        return None
    
    def get_user_alarms(self, user_id):
        """Get all alarms for a user"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM alarms WHERE user_id = ? ORDER BY time', (user_id,))
        alarms = [DBAlarm(row) for row in cursor.fetchall()]
        conn.close()
        return alarms
    
    def get_all_alarms(self):
        """Get all alarms (admin only)"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM alarms ORDER BY time')
        alarms = [DBAlarm(row) for row in cursor.fetchall()]
        conn.close()
        return alarms
    
    def update_alarm(self, alarm_id, user_id=None, time_str=None, days=None, 
                    enabled=None, label=None, sound_file=None, 
                    snooze_allowed=None, snooze_duration=None):
        """Update an existing alarm"""
        alarm = self.get_alarm(alarm_id)
        if not alarm:
            return None
        
        # Check permission (user can only update their own alarms unless admin)
        # This will be checked in the API layer
        
        conn = get_db()
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        if time_str is not None:
            updates.append('time = ?')
            values.append(time_str)
        if days is not None:
            updates.append('days = ?')
            values.append(json.dumps(days) if days else None)
        if enabled is not None:
            updates.append('enabled = ?')
            values.append(enabled)
        if label is not None:
            updates.append('label = ?')
            values.append(label)
        if sound_file is not None:
            updates.append('sound_file = ?')
            values.append(sound_file)
        if snooze_allowed is not None:
            updates.append('snooze_allowed = ?')
            values.append(snooze_allowed)
        if snooze_duration is not None:
            updates.append('snooze_duration = ?')
            values.append(snooze_duration)
        
        if updates:
            values.append(alarm_id)
            cursor.execute(f'''
                UPDATE alarms SET {', '.join(updates)} WHERE id = ?
            ''', values)
            conn.commit()
        
        conn.close()
        return self.get_alarm(alarm_id)
    
    def delete_alarm(self, alarm_id):
        """Delete an alarm"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM alarms WHERE id = ?', (alarm_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    def check_alarms(self, current_time=None):
        """Check which alarms should trigger"""
        if current_time is None:
            current_time = datetime.now()
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM alarms WHERE enabled = 1')
        alarms = [DBAlarm(row) for row in cursor.fetchall()]
        conn.close()
        
        triggered = []
        for alarm in alarms:
            if alarm.should_trigger(current_time):
                triggered.append(alarm)
        
        return triggered
    
    def snooze_alarm(self, alarm_id, minutes=None):
        """Snooze an alarm"""
        alarm = self.get_alarm(alarm_id)
        if not alarm:
            return False
        
        if not alarm.snooze_allowed:
            return False
        
        if minutes is None:
            minutes = alarm.snooze_duration
        
        snooze_until = datetime.now() + timedelta(minutes=minutes)
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE alarms SET snooze_until = ? WHERE id = ?
        ''', (snooze_until.isoformat(), alarm_id))
        conn.commit()
        conn.close()
        
        return True
    
    def dismiss_alarm(self, alarm_id):
        """Dismiss an alarm"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE alarms 
            SET last_triggered = CURRENT_TIMESTAMP, snooze_until = NULL 
            WHERE id = ?
        ''', (alarm_id,))
        dismissed = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return dismissed


"""
Database management for users, alarms, settings, and sounds
"""
import sqlite3
import os
import hashlib
import secrets
from datetime import datetime
from threading import Lock

DATABASE_FILE = 'wecker.db'
db_lock = Lock()


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database with all tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Alarms table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alarms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            time TEXT NOT NULL,
            days TEXT,
            enabled INTEGER DEFAULT 1,
            label TEXT,
            sound_file TEXT,
            snooze_allowed INTEGER DEFAULT 1,
            snooze_duration INTEGER DEFAULT 5,
            snooze_until TIMESTAMP,
            last_triggered TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sounds table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            user_id INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    
    # Create default admin user if no users exist
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        # Default admin: admin / admin (should be changed!)
        password_hash = hash_password('admin')
        cursor.execute('''
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
        ''', ('admin', password_hash, 'admin'))
        conn.commit()
        print("Default admin user created: username='admin', password='admin'")
        print("WARNING: Please change the default password!")
    
    conn.close()


def hash_password(password):
    """Hash a password using SHA256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"


def verify_password(password, password_hash):
    """Verify a password against a hash"""
    try:
        salt, stored_hash = password_hash.split(':')
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return computed_hash == stored_hash
    except:
        return False


class UserManager:
    def __init__(self):
        init_database()
    
    def create_user(self, username, password, role='user'):
        """Create a new user"""
        if role not in ['admin', 'user', 'guest']:
            raise ValueError("Invalid role. Must be 'admin', 'user', or 'guest'")
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            password_hash = hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            ''', (username, password_hash, role))
            conn.commit()
            user_id = cursor.lastrowid
            return user_id
        except sqlite3.IntegrityError:
            raise ValueError("Username already exists")
        finally:
            conn.close()
    
    def authenticate(self, username, password):
        """Authenticate a user"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and verify_password(password, user['password_hash']):
            # Update last login
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user['id'],))
            conn.commit()
            conn.close()
            
            return {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
        return None
    
    def get_user(self, user_id):
        """Get user by ID"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
        return None
    
    def change_password(self, user_id, old_password, new_password):
        """Change user password"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user or not verify_password(old_password, user['password_hash']):
            conn.close()
            return False
        
        new_hash = hash_password(new_password)
        cursor.execute('''
            UPDATE users SET password_hash = ? WHERE id = ?
        ''', (new_hash, user_id))
        conn.commit()
        conn.close()
        return True
    
    def get_all_users(self):
        """Get all users (admin only)"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, role, created_at, last_login FROM users')
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users


class SessionManager:
    def __init__(self):
        init_database()
    
    def create_session(self, user_id, duration_hours=24):
        """Create a new session"""
        session_id = secrets.token_urlsafe(32)
        conn = get_db()
        cursor = conn.cursor()
        
        from datetime import timedelta
        expires_at = datetime.now() + timedelta(hours=duration_hours)
        
        cursor.execute('''
            INSERT INTO sessions (session_id, user_id, expires_at)
            VALUES (?, ?, ?)
        ''', (session_id, user_id, expires_at))
        conn.commit()
        conn.close()
        
        return session_id
    
    def get_session(self, session_id):
        """Get session and user info"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, u.username, u.role
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_id = ? AND s.expires_at > CURRENT_TIMESTAMP
        ''', (session_id,))
        session = cursor.fetchone()
        conn.close()
        
        if session:
            return {
                'session_id': session['session_id'],
                'user_id': session['user_id'],
                'username': session['username'],
                'role': session['role']
            }
        return None
    
    def delete_session(self, session_id):
        """Delete a session"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
        conn.commit()
        conn.close()
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP')
        conn.commit()
        conn.close()


class SettingsManager:
    def __init__(self):
        init_database()
    
    def get_setting(self, key, default=None):
        """Get a setting value"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result['value']
        return default
    
    def set_setting(self, key, value):
        """Set a setting value"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        conn.commit()
        conn.close()
    
    def get_all_settings(self):
        """Get all settings"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM settings')
        settings = {row['key']: row['value'] for row in cursor.fetchall()}
        conn.close()
        return settings


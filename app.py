"""
Raspberry Pi Wecker - Main Application
Web server with authentication, roles, REST API and web interface
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from functools import wraps
from datetime import datetime, timedelta
from functools import wraps
import threading
import time
import atexit
import os
from config import WEB_PORT, WEB_HOST, DEBUG_MODE

# CORS für API-Zugriff von überall
from flask_cors import CORS

from database import UserManager, SessionManager, SettingsManager
from db_alarm_manager import DBAlarmManager
from display_controller import TM1637Display
from hardware_controller import HardwareController
from sound_manager import SoundManager, SOUNDS_DIR

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Change this in production!

# Session-Konfiguration für Cross-Origin-Zugriff
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Oder 'None' für Cross-Origin
app.config['SESSION_COOKIE_SECURE'] = False  # True für HTTPS
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# CORS für API-Zugriff von überall (wichtig für öffentlichen Zugriff)
try:
    from flask_cors import CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "supports_credentials": True,
            "max_age": 3600
        },
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "supports_credentials": True
        }
    })
except ImportError:
    print("Warning: flask-cors not installed. CORS disabled. Install with: pip install flask-cors")

# Initialize components
user_manager = UserManager()
session_manager = SessionManager()
settings_manager = SettingsManager()
alarm_manager = DBAlarmManager()
sound_manager = SoundManager()

display = None
hardware = None
alarm_check_thread = None
display_update_thread = None
running = True
active_alarm = None

# Initialize hardware (with error handling for non-RPi environments)
try:
    display = TM1637Display()
    hardware = HardwareController(button_callback=handle_button_press)
except Exception as e:
    print(f"Warning: Could not initialize hardware: {e}")
    print("Running in simulation mode (hardware disabled)")


def handle_button_press():
    """Handle button press - dismiss active alarm"""
    global active_alarm
    if active_alarm:
        alarm_manager.dismiss_alarm(active_alarm.id)
        if hardware:
            hardware.stop_sound()
        active_alarm = None
        print("Alarm dismissed via button")


def check_alarms_loop():
    """Background thread to check for alarms"""
    global active_alarm, running
    
    while running:
        try:
            current_time = datetime.now()
            triggered = alarm_manager.check_alarms(current_time)
            
            # Handle triggered alarms
            for alarm in triggered:
                if active_alarm is None or active_alarm.id != alarm.id:
                    active_alarm = alarm
                    print(f"Alarm triggered: {alarm.label or alarm.time_str}")
                    
                    if hardware:
                        # Get sound file path if custom sound is set
                        sound_file = None
                        if alarm.sound_file:
                            try:
                                sound_id = int(alarm.sound_file) if isinstance(alarm.sound_file, str) and alarm.sound_file.isdigit() else alarm.sound_file
                                sound_info = sound_manager.get_sound(sound_id)
                                if sound_info and os.path.exists(sound_info['filepath']):
                                    sound_file = sound_info['filepath']
                            except (ValueError, TypeError) as e:
                                print(f"Error loading sound file: {e}")
                        
                        hardware.start_alarm_sound(sound_file=sound_file)
            
            # Check if active alarm should stop
            if active_alarm:
                alarm_obj = alarm_manager.get_alarm(active_alarm.id)
                if alarm_obj and not alarm_obj.should_trigger():
                    if alarm_obj.snooze_until and datetime.now() < alarm_obj.snooze_until:
                        if hardware:
                            hardware.stop_sound()
                    elif alarm_obj.last_triggered and alarm_obj.last_triggered.date() == datetime.now().date():
                        if hardware:
                            hardware.stop_sound()
                        active_alarm = None
            
            time.sleep(1)
        except Exception as e:
            print(f"Error in alarm check loop: {e}")
            time.sleep(5)


def update_display_loop():
    """Background thread to update display"""
    global running, active_alarm
    
    while running:
        try:
            if display:
                current_time = datetime.now()
                
                if active_alarm:
                    display.show_time(
                        current_time.hour,
                        current_time.minute,
                        colon=(int(time.time()) % 2 == 0)
                    )
                else:
                    display.show_time(
                        current_time.hour,
                        current_time.minute,
                        colon=True
                    )
            
            time.sleep(1)
        except Exception as e:
            print(f"Error in display update loop: {e}")
            time.sleep(5)


# Start background threads
if display or hardware:
    alarm_check_thread = threading.Thread(target=check_alarms_loop, daemon=True)
    alarm_check_thread.start()
    
    if display:
        display_update_thread = threading.Thread(target=update_display_loop, daemon=True)
        display_update_thread.start()


# Cleanup function
def cleanup():
    """Cleanup on exit"""
    global running
    running = False
    if hardware:
        hardware.cleanup()
    if display:
        display.cleanup()


atexit.register(cleanup)


# Authentication and Authorization Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Prüfe ob es eine API-Anfrage ist
        is_api = request.path.startswith('/api/') or request.is_json or request.headers.get('Content-Type') == 'application/json'
        
        session_id = session.get('session_id')
        if not session_id:
            if is_api:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        
        user_info = session_manager.get_session(session_id)
        if not user_info:
            session.clear()
            if is_api:
                return jsonify({'error': 'Session expired'}), 401
            return redirect(url_for('login'))
        
        request.current_user = user_info
        return f(*args, **kwargs)
    return decorated_function


def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user_role = request.current_user.get('role')
            if user_role not in allowed_roles:
                if request.is_json:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Web Interface Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        user = user_manager.authenticate(username, password)
        if user:
            session_id = session_manager.create_session(user['id'])
            session['session_id'] = session_id
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'role': user['role']
                    }
                })
            return redirect(url_for('index'))
        else:
            if request.is_json:
                return jsonify({'error': 'Invalid credentials'}), 401
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout"""
    session_id = session.get('session_id')
    if session_id:
        session_manager.delete_session(session_id)
    session.clear()
    
    if request.is_json:
        return jsonify({'success': True})
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    """Main web interface"""
    return render_template('index.html', user=request.current_user)


# API Routes - Authentication
@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def api_login():
    """API login endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    user = user_manager.authenticate(username, password)
    if user:
        session_id = session_manager.create_session(user['id'])
        session['session_id'] = session_id
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session.permanent = True
        
        response = jsonify({
            'success': True,
            'session_id': session_id,
            'user': user
        })
        return response
    
    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def api_logout():
    """API logout endpoint"""
    session_id = session.get('session_id')
    if session_id:
        session_manager.delete_session(session_id)
    session.clear()
    return jsonify({'success': True})


@app.route('/api/auth/me', methods=['GET'])
@login_required
def api_me():
    """Get current user info"""
    return jsonify(request.current_user)


# API Routes - Alarms
@app.route('/api/alarms', methods=['GET'])
@login_required
def get_alarms():
    """Get all alarms (user sees own, admin sees all)"""
    user = request.current_user
    
    if user['role'] == 'admin':
        alarms = alarm_manager.get_all_alarms()
    else:
        alarms = alarm_manager.get_user_alarms(user['id'])
    
    return jsonify({
        'alarms': [a.to_dict() for a in alarms],
        'active_alarm': active_alarm.to_dict() if active_alarm else None
    })


@app.route('/api/alarms', methods=['POST'])
@login_required
def create_alarm():
    """Create a new alarm"""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    user = request.current_user
    
    time_str = data.get('time')
    days = data.get('days', [])
    enabled = data.get('enabled', True)
    label = data.get('label', '')
    sound_file = data.get('sound_file')
    snooze_allowed = data.get('snooze_allowed', True)
    snooze_duration = data.get('snooze_duration', 5)
    
    if not time_str:
        return jsonify({'error': 'Time is required'}), 400
    
    # Validierung: days muss Liste sein oder None
    if days is not None and not isinstance(days, list):
        days = []
    
    try:
        alarm = alarm_manager.add_alarm(
            user['id'], time_str, days, enabled, label,
            sound_file, snooze_allowed, snooze_duration
        )
        return jsonify(alarm.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error creating alarm: {e}")
        return jsonify({'error': 'Failed to create alarm'}), 500


@app.route('/api/alarms/<int:alarm_id>', methods=['PUT'])
@login_required
def update_alarm(alarm_id):
    """Update an existing alarm"""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    user = request.current_user
    alarm = alarm_manager.get_alarm(alarm_id)
    
    if not alarm:
        return jsonify({'error': 'Alarm not found'}), 404
    
    # Check permission
    if user['role'] != 'admin' and alarm.user_id != user['id']:
        return jsonify({'error': 'Permission denied'}), 403
    
    # Validierung: days muss Liste sein oder None
    days = data.get('days')
    if days is not None and not isinstance(days, list):
        days = []
    
    try:
        alarm = alarm_manager.update_alarm(
            alarm_id,
            time_str=data.get('time'),
            days=days,
            enabled=data.get('enabled'),
            label=data.get('label'),
            sound_file=data.get('sound_file'),
            snooze_allowed=data.get('snooze_allowed'),
            snooze_duration=data.get('snooze_duration')
        )
        
        if not alarm:
            return jsonify({'error': 'Failed to update alarm'}), 500
        
        return jsonify(alarm.to_dict())
    except Exception as e:
        print(f"Error updating alarm: {e}")
        return jsonify({'error': 'Failed to update alarm'}), 500


@app.route('/api/alarms/<int:alarm_id>', methods=['DELETE'])
@login_required
def delete_alarm(alarm_id):
    """Delete an alarm"""
    user = request.current_user
    alarm = alarm_manager.get_alarm(alarm_id)
    
    if not alarm:
        return jsonify({'error': 'Alarm not found'}), 404
    
    # Check permission
    if user['role'] != 'admin' and alarm.user_id != user['id']:
        return jsonify({'error': 'Permission denied'}), 403
    
    if alarm_manager.delete_alarm(alarm_id):
        return jsonify({'success': True}), 200
    return jsonify({'error': 'Failed to delete alarm'}), 500


@app.route('/api/alarms/<int:alarm_id>/snooze', methods=['POST'])
@login_required
def snooze_alarm(alarm_id):
    """Snooze an alarm"""
    alarm = alarm_manager.get_alarm(alarm_id)
    if not alarm:
        return jsonify({'error': 'Alarm not found'}), 404
    
    if not alarm.snooze_allowed:
        return jsonify({'error': 'Snooze not allowed for this alarm'}), 400
    
    # JSON-Daten optional (Standard: 5 Minuten)
    if request.is_json:
        data = request.get_json() or {}
        minutes = data.get('minutes')
    else:
        minutes = None
    
    if alarm_manager.snooze_alarm(alarm_id, minutes):
        global active_alarm
        if active_alarm and active_alarm.id == alarm_id:
            if hardware:
                hardware.stop_sound()
            active_alarm = None
        return jsonify({'success': True}), 200
    return jsonify({'error': 'Failed to snooze alarm'}), 500


@app.route('/api/alarms/<int:alarm_id>/dismiss', methods=['POST'])
@login_required
def dismiss_alarm(alarm_id):
    """Dismiss an alarm"""
    if alarm_manager.dismiss_alarm(alarm_id):
        global active_alarm
        if active_alarm and active_alarm.id == alarm_id:
            if hardware:
                hardware.stop_sound()
            active_alarm = None
        return jsonify({'success': True}), 200
    return jsonify({'error': 'Alarm not found'}), 404


# API Routes - Sounds
@app.route('/api/sounds', methods=['GET'])
@login_required
def get_sounds():
    """Get all sounds (user sees own, admin sees all)"""
    user = request.current_user
    
    if user['role'] == 'admin':
        sounds = sound_manager.get_all_sounds()
    else:
        sounds = sound_manager.get_user_sounds(user['id'])
    
    return jsonify({'sounds': sounds})


@app.route('/api/sounds', methods=['POST'])
@login_required
def upload_sound():
    """Upload a sound file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file size (max 10MB)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        return jsonify({'error': 'File too large. Maximum size: 10MB'}), 400
    
    # Check file extension
    allowed_extensions = {'wav', 'mp3', 'ogg', 'flac'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}), 400
    
    try:
        user = request.current_user
        sound = sound_manager.upload_sound(file, user['id'], file.filename)
        return jsonify(sound), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error uploading sound: {e}")
        return jsonify({'error': 'Upload failed'}), 500


@app.route('/api/sounds/<int:sound_id>', methods=['DELETE'])
@login_required
def delete_sound(sound_id):
    """Delete a sound file"""
    user = request.current_user
    
    # Check permission (admin can delete any, user can only delete own)
    if user['role'] != 'admin':
        sounds = sound_manager.get_user_sounds(user['id'])
        if not any(s['id'] == sound_id for s in sounds):
            return jsonify({'error': 'Permission denied'}), 403
    
    if sound_manager.delete_sound(sound_id, user['id'] if user['role'] != 'admin' else None):
        return jsonify({'success': True}), 200
    return jsonify({'error': 'Sound not found'}), 404


@app.route('/sounds/<filename>')
@login_required
def serve_sound(filename):
    """Serve sound files"""
    return send_from_directory(SOUNDS_DIR, filename)


# API Routes - Users (Admin only)
@app.route('/api/users', methods=['GET'])
@role_required('admin')
def get_users():
    """Get all users (admin only)"""
    users = user_manager.get_all_users()
    return jsonify({'users': users})


@app.route('/api/users', methods=['POST'])
@role_required('admin')
def create_user():
    """Create a new user (admin only)"""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    try:
        user_id = user_manager.create_user(username, password, role)
        return jsonify({'id': user_id, 'username': username, 'role': role}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# API Routes - Status
@app.route('/api/status', methods=['GET'])
@login_required
def get_status():
    """Get system status"""
    current_time = datetime.now()
    user = request.current_user
    
    try:
        if user['role'] == 'admin':
            alarm_count = len(alarm_manager.get_all_alarms())
        else:
            alarm_count = len(alarm_manager.get_user_alarms(user['id']))
        
        return jsonify({
            'current_time': current_time.isoformat(),
            'alarm_count': alarm_count,
            'active_alarm': active_alarm.to_dict() if active_alarm else None,
            'hardware_available': display is not None and hardware is not None,
            'user': user
        })
    except Exception as e:
        print(f"Error getting status: {e}")
        return jsonify({
            'current_time': current_time.isoformat(),
            'alarm_count': 0,
            'active_alarm': None,
            'hardware_available': False,
            'user': user,
            'error': 'Failed to get full status'
        }), 500


@app.route('/api/time', methods=['GET'])
def get_time():
    """Get current time"""
    return jsonify({
        'time': datetime.now().strftime('%H:%M:%S'),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'iso': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print(f"Starting Wecker server on {WEB_HOST}:{WEB_PORT}")
    print("=" * 60)
    print("Web interface:")
    print(f"  - Lokal: http://localhost:{WEB_PORT}/")
    print(f"  - Netzwerk: http://<raspberry-pi-ip>:{WEB_PORT}/")
    print("=" * 60)
    print("Default admin: username='admin', password='admin'")
    print("WARNING: Change default password immediately!")
    print("=" * 60)
    print("Für öffentlichen Zugriff:")
    print("  1. Port-Forwarding im Router einrichten")
    print("  2. Oder ngrok verwenden: ngrok http 5000")
    print("  3. Siehe INSTALLATION.md für Details")
    print("=" * 60)
    app.run(host=WEB_HOST, port=WEB_PORT, debug=DEBUG_MODE, threaded=True)

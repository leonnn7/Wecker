"""
Sound file management and playback
"""
import os
import shutil
from datetime import datetime
from database import get_db

SOUNDS_DIR = 'sounds'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac'}


def init_sounds_directory():
    """Initialize sounds directory"""
    if not os.path.exists(SOUNDS_DIR):
        os.makedirs(SOUNDS_DIR)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class SoundManager:
    def __init__(self):
        init_sounds_directory()
        from database import init_database
        init_database()
    
    def upload_sound(self, file, user_id, original_filename):
        """Upload and save a sound file"""
        if not allowed_file(original_filename):
            raise ValueError(f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = original_filename.rsplit('.', 1)[1].lower()
        filename = f"{timestamp}_{user_id}.{ext}"
        filepath = os.path.join(SOUNDS_DIR, filename)
        
        # Save file
        file.save(filepath)
        
        # Save to database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sounds (filename, original_filename, user_id)
            VALUES (?, ?, ?)
        ''', (filename, original_filename, user_id))
        sound_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'id': sound_id,
            'filename': filename,
            'original_filename': original_filename,
            'filepath': filepath
        }
    
    def get_sound(self, sound_id):
        """Get sound info by ID"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sounds WHERE id = ?', (sound_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row['id'],
                'filename': row['filename'],
                'original_filename': row['original_filename'],
                'filepath': os.path.join(SOUNDS_DIR, row['filename'])
            }
        return None
    
    def get_user_sounds(self, user_id):
        """Get all sounds uploaded by a user"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM sounds WHERE user_id = ? ORDER BY uploaded_at DESC
        ''', (user_id,))
        sounds = []
        for row in cursor.fetchall():
            sounds.append({
                'id': row['id'],
                'filename': row['filename'],
                'original_filename': row['original_filename'],
                'filepath': os.path.join(SOUNDS_DIR, row['filename']),
                'uploaded_at': row['uploaded_at']
            })
        conn.close()
        return sounds
    
    def get_all_sounds(self):
        """Get all sounds (admin only)"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sounds ORDER BY uploaded_at DESC')
        sounds = []
        for row in cursor.fetchall():
            sounds.append({
                'id': row['id'],
                'filename': row['filename'],
                'original_filename': row['original_filename'],
                'filepath': os.path.join(SOUNDS_DIR, row['filename']),
                'user_id': row['user_id'],
                'uploaded_at': row['uploaded_at']
            })
        conn.close()
        return sounds
    
    def delete_sound(self, sound_id, user_id=None):
        """Delete a sound file"""
        conn = get_db()
        cursor = conn.cursor()
        
        # Get sound info
        if user_id:
            cursor.execute('SELECT * FROM sounds WHERE id = ? AND user_id = ?', 
                         (sound_id, user_id))
        else:
            cursor.execute('SELECT * FROM sounds WHERE id = ?', (sound_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False
        
        # Delete file
        filepath = os.path.join(SOUNDS_DIR, row['filename'])
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Delete from database
        cursor.execute('DELETE FROM sounds WHERE id = ?', (sound_id,))
        conn.commit()
        conn.close()
        
        return True


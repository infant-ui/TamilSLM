import sqlite3
import os
from datetime import datetime

# Path relative to backend/generation-service/
DB_PATH = os.path.join(os.path.dirname(__file__), "images.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_prompt TEXT NOT NULL,
            enhanced_prompt TEXT NOT NULL,
            medium TEXT NOT NULL,
            image_path TEXT NOT NULL,
            generation_time_ms INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_image_generation(user_prompt: str, enhanced_prompt: str, medium: str, image_path: str, generation_time_ms: int, status: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO images (user_prompt, enhanced_prompt, medium, image_path, generation_time_ms, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_prompt, enhanced_prompt, medium, image_path, generation_time_ms, status))
    conn.commit()
    conn.close()

def get_cached_image(user_prompt: str, medium: str) -> str:
    """
    Simple exact-match caching.
    Returns the image_path if found, else None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Check if a successful generation already exists for this exact prompt and medium
    cursor.execute('''
        SELECT image_path FROM images
        WHERE user_prompt = ? AND medium = ? AND status = 'success'
        ORDER BY created_at DESC LIMIT 1
    ''', (user_prompt, medium))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Initialize on import
init_db()

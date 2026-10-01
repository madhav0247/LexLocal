import sqlite3
import json
import os
import logging
from datetime import datetime
from src.config import settings

def get_db():
    os.makedirs(settings.paths.data_dir, exist_ok=True)
    db_path = os.path.join(settings.paths.data_dir, "meta.sqlite")
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT,
            payload_json TEXT
        )
    ''')
    conn.commit()
    return conn

def log_event(event_type: str, payload: dict):
    os.makedirs(os.path.join(settings.paths.data_dir, "logs"), exist_ok=True)
    log_file = os.path.join(settings.paths.data_dir, "logs", "audit.log")
    
    ts = datetime.now().isoformat()
    log_line = f"[{ts}] {event_type}: {json.dumps(payload)}\n"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_line)
        
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_log (event_type, payload_json) VALUES (?, ?)",
            (event_type, json.dumps(payload))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Failed to write audit log to sqlite: {e}")

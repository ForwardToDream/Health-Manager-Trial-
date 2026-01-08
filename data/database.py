import sqlite3
import json
import os
import datetime
import shutil

DB_FILE = "user_data.db"
JSON_FILE = "user_data.json"

_db_initialized = False

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    global _db_initialized
    if _db_initialized:
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kv_store (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            date TEXT PRIMARY KEY,
            summary TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    
    _check_migration()
    
    _db_initialized = True

def _check_migration():
    if os.path.exists(JSON_FILE) and not os.path.exists(DB_FILE + ".migrated"):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM kv_store")
            if cursor.fetchone()[0] == 0:
                print("Migrating from user_data.json...")
                with open(JSON_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                history = data.pop("history", {})
                
                for k, v in data.items():
                    cursor.execute(
                        "INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)",
                        (k, json.dumps(v, ensure_ascii=False))
                    )
                
                for date_str, summary in history.items():
                    cursor.execute(
                        "INSERT OR REPLACE INTO history (date, summary) VALUES (?, ?)",
                        (date_str, json.dumps(summary, ensure_ascii=False))
                    )
                
                conn.commit()
                print("Migration successful.")
                
                shutil.copy2(JSON_FILE, JSON_FILE + ".bak")
                with open(DB_FILE + ".migrated", "w") as f:
                    f.write("Migrated on " + datetime.datetime.now().isoformat())
                    
            conn.close()
        except Exception as e:
            print(f"Migration failed: {e}")

def get_all_data():
    if not _db_initialized:
        init_db()

    conn = get_db_connection()
    cursor = conn.cursor()
    
    result = {}
    
    cursor.execute("SELECT key, value FROM kv_store")
    for row in cursor.fetchall():
        try:
            result[row['key']] = json.loads(row['value'])
        except json.JSONDecodeError:
            result[row['key']] = row['value']
        
    conn.close()
    return result

def save_key(key, value):
    if not _db_initialized:
        init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)",
        (key, json.dumps(value, ensure_ascii=False))
    )
    
    conn.commit()
    conn.close()

def save_history(date_str, summary):
    if not _db_initialized:
        init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT OR REPLACE INTO history (date, summary) VALUES (?, ?)",
        (date_str, json.dumps(summary, ensure_ascii=False))
    )
    
    conn.commit()
    conn.close()

def save_multiple_keys(data_dict):
    if not _db_initialized:
        init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for k, v in data_dict.items():
            if k == "history":
                if isinstance(v, dict):
                    for h_date, h_summary in v.items():
                        cursor.execute(
                            "INSERT OR REPLACE INTO history (date, summary) VALUES (?, ?)",
                            (h_date, json.dumps(h_summary, ensure_ascii=False))
                        )
            else:
                cursor.execute(
                    "INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)",
                    (k, json.dumps(v, ensure_ascii=False))
                )
        conn.commit()
    except Exception as e:
        print(f"Error saving multiple keys: {e}")
    finally:
        conn.close()

def get_month_history(year, month):
    if not _db_initialized:
        init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    prefix = f"{year:04d}-{month:02d}%"
    cursor.execute("SELECT date, summary FROM history WHERE date LIKE ?", (prefix,))
    
    result = {}
    for row in cursor.fetchall():
        try:
            result[row['date']] = json.loads(row['summary'])
        except: pass
    
    conn.close()
    return result

def get_daily_history(date_str):
    if not _db_initialized:
        init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT summary FROM history WHERE date = ?", (date_str,))
    row = cursor.fetchone()
    
    result = {}
    if row:
        try:
            result = json.loads(row['summary'])
        except: pass
    
    conn.close()
    return result

import sqlite3
from datetime import datetime

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    joined_at TEXT,
    referred_by INTEGER,
    referrals INTEGER DEFAULT 0
)
""")

conn.commit()

def add_user(user_id, name, ref=None):
    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if cursor.fetchone():
        return False

    cursor.execute(
        "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
        (user_id, name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ref, 0)
    )

    if ref:
        cursor.execute("UPDATE users SET referrals = referrals + 1 WHERE user_id=?", (ref,))

    conn.commit()
    return True

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()
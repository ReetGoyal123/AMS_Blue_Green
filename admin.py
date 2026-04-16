"""
Run this once to create/reset the admin account.
Place it in the same folder as your attendance.db and run:
    python admin.py
"""
import sqlite3
import hashlib

DATABASE_NAME = "attendance.db"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect(DATABASE_NAME)
cursor = conn.cursor()

# Make sure users table exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'student',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Remove any existing 'admin' username or the target email to avoid conflicts
cursor.execute("DELETE FROM users WHERE username = 'admin' OR email = 'reet114@igdtuw.ac.in'")

# Insert fresh admin
cursor.execute(
    "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
    ("admin", "reet114@igdtuw.ac.in", hash_password("admin123"), "admin")
)
conn.commit()
conn.close()

print("Admin account created successfully.")
print("Username: admin")
print("Password: admin123")
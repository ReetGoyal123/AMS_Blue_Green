"""
Database module for handling SQLite operations
"""
import sqlite3
import os
import hashlib
from datetime import datetime
from contextlib import contextmanager

DATABASE_NAME = "attendance.db"

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def _hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    with get_db_connection() as conn:
        cursor = conn.cursor()

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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT DEFAULT 'Present',
                marked_by TEXT DEFAULT 'self',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, date)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                filename TEXT,
                filepath TEXT,
                due_date TEXT,
                uploaded_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                posted_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

        # Seed default admin
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                ("admin", "reet114@igdtuw.ac.in", _hash("admin123"), "admin")
            )
            conn.commit()

    os.makedirs("uploads", exist_ok=True)


# ── USER FUNCTIONS ──

def create_user(username, email, password_hash, role="student"):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                (username, email, password_hash, role)
            )
            conn.commit()
            return True, "User created successfully"
    except sqlite3.IntegrityError as e:
        if "username" in str(e): return False, "Username already exists"
        if "email" in str(e): return False, "Email already exists"
        return False, "Error creating user"

def get_user_by_username(username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        return dict(user) if user else None

def get_user_by_id(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        return dict(user) if user else None

def get_all_users():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

def get_all_students():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, created_at FROM users WHERE role = 'student' ORDER BY username")
        return [dict(row) for row in cursor.fetchall()]

def update_user_password(user_id, new_password_hash):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))
        conn.commit()
        return True

def delete_user(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM attendance WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True


# ── ATTENDANCE FUNCTIONS ──

def mark_attendance(user_id, marked_by="self"):
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO attendance (user_id, date, time, status, marked_by) VALUES (?, ?, ?, ?, ?)",
                (user_id, current_date, current_time, "Present", marked_by)
            )
            conn.commit()
            return True, "Attendance marked successfully"
    except sqlite3.IntegrityError:
        return False, "Attendance already marked for today"

def mark_attendance_for_date(user_id, date_str, marked_by="admin"):
    try:
        current_time = datetime.now().strftime("%H:%M:%S")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO attendance (user_id, date, time, status, marked_by) VALUES (?, ?, ?, ?, ?)",
                (user_id, date_str, current_time, "Present", marked_by)
            )
            conn.commit()
            return True, "Attendance marked successfully"
    except sqlite3.IntegrityError:
        return False, "Attendance already marked for this date"

def get_user_attendance(user_id, start_date=None, end_date=None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM attendance WHERE user_id = ?"
        params = [user_id]
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        query += " ORDER BY date DESC, time DESC"
        cursor.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]

def get_attendance_stats(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM attendance WHERE user_id = ?", (user_id,))
        total = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as present FROM attendance WHERE user_id = ? AND status='Present'", (user_id,))
        present = cursor.fetchone()['present']
        pct = round(present / total * 100, 2) if total > 0 else 0
        return {'total_days': total, 'present_days': present, 'percentage': pct}

def get_all_attendance():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, u.username, u.email
            FROM attendance a JOIN users u ON a.user_id = u.id
            ORDER BY a.date DESC, a.time DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

def get_student_attendance_summary():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.created_at,
                COUNT(a.id) as total_days,
                SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) as present_days
            FROM users u
            LEFT JOIN attendance a ON u.id = a.user_id
            WHERE u.role = 'student'
            GROUP BY u.id ORDER BY u.username
        """)
        result = []
        for row in cursor.fetchall():
            r = dict(row)
            r['percentage'] = round(r['present_days'] / r['total_days'] * 100, 2) if r['total_days'] > 0 else 0.0
            result.append(r)
        return result


# ── ASSIGNMENT FUNCTIONS ──

def add_assignment(title, description, filename, filepath, due_date, uploaded_by):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO assignments (title, description, filename, filepath, due_date, uploaded_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, description, filename, filepath, due_date, uploaded_by))
        conn.commit()
        return True, "Assignment uploaded"

def get_all_assignments():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assignments ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

def delete_assignment(assignment_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT filepath FROM assignments WHERE id = ?", (assignment_id,))
        row = cursor.fetchone()
        if row and row['filepath'] and os.path.exists(row['filepath']):
            os.remove(row['filepath'])
        cursor.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
        conn.commit()
        return True


# ── NOTICE FUNCTIONS ──

def add_notice(title, body, posted_by):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notices (title, body, posted_by) VALUES (?, ?, ?)",
            (title, body, posted_by)
        )
        conn.commit()
        return True

def get_all_notices():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notices ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

def delete_notice(notice_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notices WHERE id = ?", (notice_id,))
        conn.commit()
        return True
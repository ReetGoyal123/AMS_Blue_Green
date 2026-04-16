"""
Database module — SQLite, no pandas dependency.
All functions return plain Python dicts / lists of dicts.
"""
import sqlite3
from datetime import datetime

DATABASE_NAME = "attendance.db"


# ─────────────────────────────────────────────────────────
# CONNECTION HELPER
# ─────────────────────────────────────────────────────────

def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row   # lets us access columns by name
    return conn


def row_to_dict(row):
    return dict(row) if row else None


def rows_to_dicts(rows):
    return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────
# INITIALISE SCHEMA
# ─────────────────────────────────────────────────────────

def init_database():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role          TEXT DEFAULT 'student',
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            date       TEXT NOT NULL,
            time       TEXT NOT NULL,
            status     TEXT DEFAULT 'present',
            marked_by  TEXT DEFAULT 'self',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE (user_id, date)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            description TEXT,
            filename    TEXT,
            filepath    TEXT,
            due_date    TEXT,
            uploaded_by TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            title      TEXT NOT NULL,
            body       TEXT NOT NULL,
            posted_by  TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────
# USER FUNCTIONS
# ─────────────────────────────────────────────────────────

def create_user(username, email, password_hash, role="student"):
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, role)
        )
        conn.commit()
        conn.close()
        return True, "User created successfully"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already taken"
        if "email" in str(e):
            return False, "Email already registered"
        return False, str(e)


def get_user_by_username(username):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return row_to_dict(row)


def get_user_by_id(user_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return row_to_dict(row)


def get_all_users():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return rows_to_dicts(rows)


def get_all_students():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM users WHERE role = 'student' ORDER BY username"
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def update_user_password(user_id, new_hash):
    conn = get_connection()
    conn.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id)
    )
    conn.commit()
    conn.close()


def delete_user(user_id):
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────
# ATTENDANCE FUNCTIONS
# ─────────────────────────────────────────────────────────

def mark_attendance(user_id, marked_by="self"):
    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO attendance (user_id, date, time, status, marked_by) VALUES (?, ?, ?, 'present', ?)",
            (user_id, today, now_time, marked_by)
        )
        conn.commit()
        conn.close()
        return True, f"Attendance marked for {today} at {now_time}"
    except sqlite3.IntegrityError:
        return False, "Attendance already marked for today"


def mark_attendance_for_date(user_id, date, marked_by="admin"):
    now_time = datetime.now().strftime("%H:%M:%S")
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO attendance (user_id, date, time, status, marked_by) VALUES (?, ?, ?, 'present', ?)",
            (user_id, date, now_time, marked_by)
        )
        conn.commit()
        conn.close()
        return True, f"Attendance marked for {date}"
    except sqlite3.IntegrityError:
        return False, f"Attendance already recorded for {date}"


def get_user_attendance(user_id, start_date=None, end_date=None):
    """Return attendance records for a user, optionally filtered by date range."""
    conn = get_connection()
    query = "SELECT * FROM attendance WHERE user_id = ?"
    params = [user_id]
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    query += " ORDER BY date DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def get_attendance_stats(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT COUNT(*) as cnt FROM attendance WHERE user_id = ? AND status = 'present'",
        (user_id,)
    ).fetchone()
    present_days = rows['cnt'] if rows else 0

    # Total = distinct days with any record (or just present count)
    total_rows = conn.execute(
        "SELECT COUNT(DISTINCT date) as cnt FROM attendance WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    total_days = total_rows['cnt'] if total_rows else 0
    conn.close()

    percentage = round(present_days / total_days * 100, 1) if total_days else 0
    return {
        'total_days': total_days,
        'present_days': present_days,
        'percentage': percentage,
    }


def get_all_attendance():
    """Return all attendance records joined with user info."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.id, a.user_id, u.username, u.email,
               a.date, a.time, a.status, a.marked_by, a.created_at
        FROM attendance a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.date DESC, u.username
    """).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def get_student_attendance_summary():
    """Return per-student attendance summary (total, present, percentage)."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT u.id, u.username, u.email,
               COUNT(DISTINCT a.date) AS total_days,
               SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS present_days
        FROM users u
        LEFT JOIN attendance a ON u.id = a.user_id
        WHERE u.role = 'student'
        GROUP BY u.id
        ORDER BY u.username
    """).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        total = d['total_days'] or 0
        present = d['present_days'] or 0
        d['percentage'] = round(present / total * 100, 1) if total else 0
        result.append(d)
    return result


# ─────────────────────────────────────────────────────────
# ASSIGNMENT FUNCTIONS
# ─────────────────────────────────────────────────────────

def add_assignment(title, description, filename, filepath, due_date, uploaded_by):
    conn = get_connection()
    conn.execute(
        "INSERT INTO assignments (title, description, filename, filepath, due_date, uploaded_by) VALUES (?, ?, ?, ?, ?, ?)",
        (title, description, filename, filepath, due_date, uploaded_by)
    )
    conn.commit()
    conn.close()


def get_all_assignments():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM assignments ORDER BY created_at DESC").fetchall()
    conn.close()
    return rows_to_dicts(rows)


def delete_assignment(assignment_id):
    conn = get_connection()
    conn.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────
# NOTICE FUNCTIONS
# ─────────────────────────────────────────────────────────

def add_notice(title, body, posted_by):
    conn = get_connection()
    conn.execute(
        "INSERT INTO notices (title, body, posted_by) VALUES (?, ?, ?)",
        (title, body, posted_by)
    )
    conn.commit()
    conn.close()


def get_all_notices():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM notices ORDER BY created_at DESC").fetchall()
    conn.close()
    return rows_to_dicts(rows)


def delete_notice(notice_id):
    conn = get_connection()
    conn.execute("DELETE FROM notices WHERE id = ?", (notice_id,))
    conn.commit()
    conn.close()
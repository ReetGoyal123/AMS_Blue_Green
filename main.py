"""
Attendance Management System
Role-based: Admin & Student portals
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import auth
import db

st.set_page_config(
    page_title="Attendance Management System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Serif+Display&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background-color: #f5f6fa; }
[data-testid="stSidebarNav"] { display: none; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

h1 { font-size: 1.6rem !important; font-weight: 700 !important; color: #111827 !important; letter-spacing: -0.02em; }
h2 { font-size: 1.2rem !important; font-weight: 600 !important; color: #111827 !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e5e7eb; }
[data-testid="stSidebar"] * { color: #374151 !important; }

.sidebar-user { padding: 1.1rem 1rem 0.9rem; border-bottom: 1px solid #f3f4f6; margin-bottom: 0.4rem; }
.sidebar-avatar {
    width: 42px; height: 42px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    color: white; font-weight: 700; font-size: 1rem; margin-bottom: 0.6rem;
}
.sidebar-name { font-size: 0.92rem; font-weight: 600; color: #111827; }
.sidebar-email { font-size: 0.74rem; color: #9ca3af; margin-top: 1px; }
.sidebar-section {
    font-size: 0.67rem; font-weight: 700; color: #9ca3af;
    text-transform: uppercase; letter-spacing: 0.09em; padding: 0.85rem 1rem 0.3rem;
}

div[data-testid="stSidebar"] .stButton > button {
    width: 100%; text-align: left !important; background: transparent;
    border: none; border-radius: 8px; padding: 0.5rem 0.85rem;
    font-size: 0.875rem; font-weight: 500; color: #374151 !important;
    margin-bottom: 1px; box-shadow: none !important; transition: background 0.12s;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: #f9fafb !important; transform: none !important; box-shadow: none !important;
}
div[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #eff6ff !important; color: #1d4ed8 !important; font-weight: 600 !important;
}

/* ── STAT CARDS ── */
.stat-card {
    background: #ffffff; border: 1px solid #e5e7eb;
    border-radius: 12px; padding: 1.15rem 1.3rem; margin-bottom: 0.75rem;
}
.stat-label { font-size: 0.7rem; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.3rem; }
.stat-value { font-size: 1.85rem; font-weight: 700; color: #111827; line-height: 1.1; letter-spacing: -0.02em; }
.stat-sub { font-size: 0.77rem; color: #9ca3af; margin-top: 0.2rem; }
.stat-good { border-top: 3px solid #10b981; }
.stat-warn { border-top: 3px solid #f59e0b; }
.stat-bad  { border-top: 3px solid #ef4444; }
.stat-blue { border-top: 3px solid #3b82f6; }
.stat-purple { border-top: 3px solid #8b5cf6; }

/* ── PAGE HEADER ── */
.page-header { margin-bottom: 1.4rem; padding-bottom: 0.9rem; border-bottom: 1px solid #f3f4f6; }
.page-title { font-size: 1.45rem; font-weight: 700; color: #111827; letter-spacing: -0.02em; margin: 0; }
.page-sub { font-size: 0.83rem; color: #9ca3af; margin-top: 3px; }

/* ── SECTION CARD ── */
.section-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.3rem 1.4rem; margin-bottom: 1rem; }

/* ── PILLS ── */
.pill-admin { display:inline-block; background:#fef2f2; color:#dc2626; border-radius:5px; padding:2px 9px; font-size:0.7rem; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; }
.pill-student { display:inline-block; background:#f0fdf4; color:#16a34a; border-radius:5px; padding:2px 9px; font-size:0.7rem; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; }

/* ── MAIN BUTTONS ── */
.stButton > button {
    border-radius: 9px; font-weight: 500; font-size: 0.88rem;
    transition: all 0.14s; border: 1px solid #d1d5db; font-family: 'DM Sans', sans-serif;
}
.stButton > button[kind="primary"] { background: #1d4ed8; border-color: #1d4ed8; color: white; }
.stButton > button[kind="primary"]:hover { background: #1e40af; box-shadow: 0 2px 8px rgba(29,78,216,0.25); transform: none; }

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea { border-radius: 9px; border-color: #d1d5db; font-size: 0.9rem; }
.stSelectbox > div > div { border-radius: 9px; border-color: #d1d5db; }

/* ── LOGIN PAGE ── */
.login-eyebrow { font-size: 0.75rem; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.3rem; }
.login-title { font-family: 'DM Serif Display', serif; font-size: 2.1rem; color: #111827; margin: 0 0 0.4rem; line-height: 1.15; }
.login-sub { font-size: 0.85rem; color: #9ca3af; margin-bottom: 1.8rem; }

/* ── PROGRESS BAR ── */
.att-bar-wrap { background:#f3f4f6; border-radius:99px; height:7px; width:100%; margin-top:4px; }
.att-bar-fill { height:7px; border-radius:99px; }

/* ── ASSIGNMENT CARD ── */
.asgn-card { background:#fff; border:1px solid #e5e7eb; border-left:4px solid #3b82f6; border-radius:10px; padding:1rem 1.2rem; margin-bottom:0.75rem; }
.asgn-title { font-weight:600; font-size:0.93rem; color:#111827; }
.asgn-meta { font-size:0.77rem; color:#9ca3af; margin-top:3px; }
.asgn-desc { font-size:0.86rem; color:#4b5563; margin-top:0.45rem; }

/* ── NOTICE CARD ── */
.notice-card { background:#fffbeb; border:1px solid #fde68a; border-left:4px solid #f59e0b; border-radius:10px; padding:0.9rem 1.2rem; margin-bottom:0.75rem; }
.notice-title { font-weight:600; font-size:0.9rem; color:#92400e; }
.notice-meta { font-size:0.74rem; color:#b45309; margin:2px 0 6px; }
.notice-body { font-size:0.84rem; color:#78350f; }

/* ── TODAY STATUS ── */
.today-present { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:0.8rem 1.1rem; margin-bottom:1rem; }
.today-absent  { background:#fffbeb; border:1px solid #fde68a; border-radius:10px; padding:0.8rem 1.1rem; margin-bottom:1rem; }

hr { border-color: #f3f4f6; }
[data-testid="stAlert"] { border-radius: 10px; }
[data-testid="stMetricValue"] { font-size:1.7rem !important; font-weight:700 !important; }
[data-testid="stDataFrame"] { border:1px solid #e5e7eb; border-radius:10px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────
def page_header(title, subtitle=""):
    st.markdown(
        f'<div class="page-header"><div class="page-title">{title}</div>'
        + (f'<div class="page-sub">{subtitle}</div>' if subtitle else '')
        + '</div>', unsafe_allow_html=True
    )

def stat_card(label, value, sub="", style="blue"):
    st.markdown(
        f'<div class="stat-card stat-{style}">'
        f'<div class="stat-label">{label}</div>'
        f'<div class="stat-value">{value}</div>'
        + (f'<div class="stat-sub">{sub}</div>' if sub else '')
        + '</div>', unsafe_allow_html=True
    )

def pct_style(pct):
    if pct >= 75: return "good"
    if pct >= 50: return "warn"
    return "bad"

def attendance_bar(pct):
    color = "#10b981" if pct >= 75 else ("#f59e0b" if pct >= 50 else "#ef4444")
    return (f'<div class="att-bar-wrap"><div class="att-bar-fill" '
            f'style="width:{min(pct,100)}%;background:{color};"></div></div>')

def init_session_state():
    defaults = {
        'authenticated': False, 'user_id': None, 'username': None,
        'email': None, 'role': None, 'page': 'login', 'login_role': None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────────────────
# AUTH PAGES
# ─────────────────────────────────────────────────────────

def login_page():
    col1, col2, col3 = st.columns([1, 1.25, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="login-eyebrow">IGDTUW &nbsp;·&nbsp; DevOps Batch</div>'
            '<div class="login-title">Welcome back</div>'
            '<div class="login-sub">Enter your credentials to access the portal</div>',
            unsafe_allow_html=True
        )

        # Role selector
        st.markdown('<p style="font-size:0.82rem;font-weight:600;color:#374151;margin-bottom:0.4rem;">Sign in as</p>', unsafe_allow_html=True)
        rc1, rc2 = st.columns(2)
        with rc1:
            if st.button("Student", use_container_width=True, key="role_s",
                         type="primary" if st.session_state.login_role == "student" else "secondary"):
                st.session_state.login_role = "student"
                st.rerun()
        with rc2:
            if st.button("Administrator", use_container_width=True, key="role_a",
                         type="primary" if st.session_state.login_role == "admin" else "secondary"):
                st.session_state.login_role = "admin"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Email address or Username")
            password = st.text_input("Password", type="password")
            col_a, col_b = st.columns(2)
            with col_a:
                st.checkbox("Remember for 30 days")
            with col_b:
                st.markdown("<div style='text-align:right;padding-top:4px;'><span style='font-size:0.82rem;color:#2563eb;font-weight:500;'>Forgot password?</span></div>", unsafe_allow_html=True)

            submitted = st.form_submit_button("Sign in", use_container_width=True, type="primary")

            if submitted:
                if not st.session_state.login_role:
                    st.error("Please select Student or Administrator above.")
                elif not username or not password:
                    st.error("Please enter your credentials.")
                else:
                    success, user, message = auth.login_user(username, password)
                    if success:
                        if user['role'] != st.session_state.login_role:
                            st.error(f"This account is registered as '{user['role']}'. Please select the correct role.")
                        else:
                            st.session_state.authenticated = True
                            st.session_state.user_id = user['id']
                            st.session_state.username = user['username']
                            st.session_state.email = user['email']
                            st.session_state.role = user['role']
                            st.session_state.page = 'dashboard'
                            st.rerun()
                    else:
                        st.error(message)

        st.markdown('<p style="text-align:center;font-size:0.84rem;color:#9ca3af;margin-top:1rem;">Don\'t have an account?</p>', unsafe_allow_html=True)
        if st.button("Create account", use_container_width=True):
            st.session_state.page = 'signup'
            st.rerun()


def signup_page():
    col1, col2, col3 = st.columns([1, 1.25, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="login-eyebrow">IGDTUW &nbsp;·&nbsp; DevOps Batch</div>'
            '<div class="login-title">Create account</div>'
            '<div class="login-sub">Student registration only. Admin accounts are created by administrators.</div>',
            unsafe_allow_html=True
        )

        with st.form("signup_form"):
            username = st.text_input("Username", placeholder="3–20 characters")
            email = st.text_input("Email address")
            password = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
            confirm = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create account", use_container_width=True, type="primary")

            if submitted:
                if not username or not email or not password or not confirm:
                    st.error("All fields are required.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = auth.signup_user(username, email, password, role="student")
                    if ok:
                        st.success("Account created. Please sign in.")
                        st.session_state.page = 'login'
                        st.rerun()
                    else:
                        st.error(msg)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Back to sign in", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()


# ─────────────────────────────────────────────────────────
# STUDENT SIDEBAR
# ─────────────────────────────────────────────────────────

def student_sidebar():
    with st.sidebar:
        initials = st.session_state.username[:2].upper()
        st.markdown(
            f'<div class="sidebar-user">'
            f'<div class="sidebar-avatar" style="background:linear-gradient(135deg,#2563eb,#7c3aed);">{initials}</div>'
            f'<div class="sidebar-name">{st.session_state.username}</div>'
            f'<div class="sidebar-email">{st.session_state.email}</div>'
            f'<div style="margin-top:7px"><span class="pill-student">Student</span></div>'
            f'</div>',
            unsafe_allow_html=True
        )

        stats = db.get_attendance_stats(st.session_state.user_id)
        pct = stats['percentage']
        st.markdown(
            f'<div style="padding:0.8rem 1rem 0.6rem;">'
            f'<div style="display:flex;justify-content:space-between;font-size:0.8rem;">'
            f'<span style="color:#6b7280;font-weight:500;">Attendance</span>'
            f'<span style="font-weight:700;color:#111827;">{pct}%</span>'
            f'</div>'
            + attendance_bar(pct) +
            f'<div style="font-size:0.73rem;color:#9ca3af;margin-top:4px;">{stats["present_days"]} of {stats["total_days"]} days present</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="sidebar-section">Menu</div>', unsafe_allow_html=True)
        nav = {
            "dashboard":   "Overview",
            "mark":        "Mark Attendance",
            "view":        "My Records",
            "assignments": "Assignments",
            "notices":     "Notices",
            "profile":     "Profile",
        }
        for key, label in nav.items():
            t = "primary" if st.session_state.page == key else "secondary"
            if st.button(label, key=f"snav_{key}", use_container_width=True, type=t):
                st.session_state.page = key
                st.rerun()

        st.markdown("---")
        if st.button("Sign Out", key="snav_logout", use_container_width=True):
            auth.logout_user(st.session_state)
            st.rerun()


# ─────────────────────────────────────────────────────────
# STUDENT PAGES
# ─────────────────────────────────────────────────────────

def student_dashboard():
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")
    page_header("Overview", f"{greeting}, {st.session_state.username}")

    stats = db.get_attendance_stats(st.session_state.user_id)
    pct = stats['percentage']

    c1, c2, c3 = st.columns(3)
    with c1:
        stat_card("Total Days", stats['total_days'], style="blue")
    with c2:
        stat_card("Days Present", stats['present_days'], style="good")
    with c3:
        note = "Good standing" if pct >= 75 else ("At risk — below 75%" if pct < 50 else "Below minimum")
        stat_card("Attendance Rate", f"{pct}%", sub=note, style=pct_style(pct))

    # Today's status banner
    today = datetime.now().strftime("%Y-%m-%d")
    today_rec = db.get_user_attendance(st.session_state.user_id, start_date=today, end_date=today)
    if today_rec:
        st.markdown(
            f'<div class="today-present">'
            f'<span style="color:#15803d;font-weight:600;font-size:0.9rem;">Attendance marked today</span>'
            f'<span style="color:#86efac;margin:0 8px;">·</span>'
            f'<span style="color:#4ade80;font-size:0.85rem;">at {today_rec[0]["time"]}</span>'
            f'</div>', unsafe_allow_html=True
        )
    else:
        st.markdown('<div class="today-absent"><span style="color:#92400e;font-weight:600;font-size:0.9rem;">You have not marked attendance today</span></div>', unsafe_allow_html=True)
        if st.button("Mark Attendance Now", type="primary"):
            ok, msg = db.mark_attendance(st.session_state.user_id)
            if ok:
                st.success(msg); st.balloons(); st.rerun()
            else:
                st.warning(msg)

    st.markdown("---")
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown("**Attendance Trend — Last 30 Days**")
        records = db.get_user_attendance(st.session_state.user_id)
        if records:
            df = pd.DataFrame(records)
            df['date'] = pd.to_datetime(df['date'])
            last30 = df[df['date'] >= datetime.now() - timedelta(days=30)]
            if not last30.empty:
                trend = last30.groupby('date').size().reset_index(name='Present')
                st.line_chart(trend.set_index('date'), color="#3b82f6")
            else:
                st.caption("No records in the last 30 days.")
        else:
            st.caption("No records yet.")

    with col_r:
        st.markdown("**Recent Activity**")
        records = db.get_user_attendance(st.session_state.user_id)
        if records:
            df = pd.DataFrame(records)[['date', 'time', 'status']].head(6)
            df.columns = ['Date', 'Time', 'Status']
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.caption("No records yet.")

    # Latest assignment + notice
    col_a, col_n = st.columns(2)
    with col_a:
        assignments = db.get_all_assignments()
        if assignments:
            a = assignments[0]
            st.markdown("---")
            st.markdown("**Latest Assignment**")
            st.markdown(
                f'<div class="asgn-card">'
                f'<div class="asgn-title">{a["title"]}</div>'
                f'<div class="asgn-meta">Due: {a["due_date"] or "No due date"} · {a["uploaded_by"]} · {a["created_at"][:10]}</div>'
                f'<div class="asgn-desc">{(a["description"] or "")[:120]}</div>'
                f'</div>', unsafe_allow_html=True
            )

    with col_n:
        notices = db.get_all_notices()
        if notices:
            n = notices[0]
            st.markdown("---")
            st.markdown("**Latest Notice**")
            st.markdown(
                f'<div class="notice-card">'
                f'<div class="notice-title">{n["title"]}</div>'
                f'<div class="notice-meta">{n["created_at"][:10]} · {n["posted_by"]}</div>'
                f'<div class="notice-body">{n["body"][:150]}{"..." if len(n["body"]) > 150 else ""}</div>'
                f'</div>', unsafe_allow_html=True
            )


def student_mark_attendance():
    page_header("Mark Attendance", "Record your presence for today")

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        today = datetime.now().strftime("%Y-%m-%d")
        today_rec = db.get_user_attendance(st.session_state.user_id, start_date=today, end_date=today)

        st.markdown(
            f'<div class="section-card" style="text-align:center;">'
            f'<div style="font-size:0.72rem;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.3rem;">Today</div>'
            f'<div style="font-size:1.85rem;font-weight:700;color:#111827;letter-spacing:-0.02em;">{datetime.now().strftime("%B %d, %Y")}</div>'
            f'<div style="color:#9ca3af;font-size:0.87rem;margin-bottom:1.2rem;">{datetime.now().strftime("%A, %I:%M %p")}</div>',
            unsafe_allow_html=True
        )

        if today_rec:
            st.success(f"Attendance marked at {today_rec[0]['time']}")
        else:
            if st.button("Mark Present", use_container_width=True, type="primary"):
                ok, msg = db.mark_attendance(st.session_state.user_id)
                if ok:
                    st.success(msg); st.balloons(); st.rerun()
                else:
                    st.warning(msg)
        st.markdown('</div>', unsafe_allow_html=True)

        # Monthly summary
        st.markdown("<br>**This Month**", unsafe_allow_html=True)
        month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        month_recs = db.get_user_attendance(st.session_state.user_id, start_date=month_start)
        days_passed = datetime.now().day
        month_pct = round(len(month_recs) / days_passed * 100, 1) if days_passed else 0
        c1, c2 = st.columns(2)
        with c1: stat_card("Present This Month", len(month_recs), style="good")
        with c2: stat_card("Monthly Rate", f"{month_pct}%", style=pct_style(month_pct))


def student_view_attendance():
    page_header("My Records", "View and export your attendance history")

    stats = db.get_attendance_stats(st.session_state.user_id)
    pct = stats['percentage']
    c1, c2, c3 = st.columns(3)
    with c1: stat_card("Total Days", stats['total_days'], style="blue")
    with c2: stat_card("Days Present", stats['present_days'], style="good")
    with c3: stat_card("Overall Rate", f"{pct}%", style=pct_style(pct))

    st.markdown("---")
    col_a, col_b, _ = st.columns([1.2, 1.2, 2])
    with col_a:
        start_date = st.date_input("From", value=datetime.now() - timedelta(days=30), max_value=datetime.now())
    with col_b:
        end_date = st.date_input("To", value=datetime.now(), max_value=datetime.now())

    records = db.get_user_attendance(st.session_state.user_id, str(start_date), str(end_date))
    if records:
        df = pd.DataFrame(records)[['date', 'time', 'status', 'marked_by']].rename(
            columns={'date': 'Date', 'time': 'Time', 'status': 'Status', 'marked_by': 'Marked By'}
        )
        st.markdown(f"<p style='color:#9ca3af;font-size:0.83rem;'>{len(df)} record(s) found</p>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Download CSV", df.to_csv(index=False),
                           f"attendance_{start_date}_to_{end_date}.csv", "text/csv")
    else:
        st.info("No records found for the selected range.")


def student_assignments():
    page_header("Assignments", "Assignments posted by your instructor")
    assignments = db.get_all_assignments()
    if not assignments:
        st.info("No assignments have been posted yet.")
        return

    for a in assignments:
        due = a['due_date'] or "No due date"
        is_due_soon = False
        if a['due_date']:
            try:
                due_dt = datetime.strptime(a['due_date'], "%Y-%m-%d")
                is_due_soon = 0 <= (due_dt - datetime.now()).days <= 3
            except: pass
        border = "#ef4444" if is_due_soon else "#3b82f6"
        tag = ' <span style="background:#fef2f2;color:#dc2626;border-radius:4px;padding:1px 7px;font-size:0.7rem;font-weight:700;margin-left:6px;">DUE SOON</span>' if is_due_soon else ""

        st.markdown(
            f'<div class="asgn-card" style="border-left-color:{border};">'
            f'<div class="asgn-title">{a["title"]}{tag}</div>'
            f'<div class="asgn-meta">Due: {due} &nbsp;·&nbsp; Posted by {a["uploaded_by"]} on {a["created_at"][:10]}</div>'
            f'<div class="asgn-desc">{a["description"] or ""}</div>'
            f'</div>', unsafe_allow_html=True
        )
        if a['filepath'] and os.path.exists(a['filepath']):
            with open(a['filepath'], "rb") as f:
                st.download_button("Download Attachment", f, a['filename'], key=f"dl_{a['id']}")
        st.markdown("<br>", unsafe_allow_html=True)


def student_notices():
    page_header("Notices", "Announcements from your instructor")
    notices = db.get_all_notices()
    if not notices:
        st.info("No notices have been posted.")
        return
    for n in notices:
        st.markdown(
            f'<div class="notice-card">'
            f'<div class="notice-title">{n["title"]}</div>'
            f'<div class="notice-meta">{n["created_at"][:10]} &nbsp;·&nbsp; {n["posted_by"]}</div>'
            f'<div class="notice-body">{n["body"]}</div>'
            f'</div>', unsafe_allow_html=True
        )


def student_profile():
    page_header("Profile", "Your account information")
    user = db.get_user_by_id(st.session_state.user_id)
    stats = db.get_attendance_stats(st.session_state.user_id)
    initials = user['username'][:2].upper()

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(
            f'<div class="section-card" style="display:flex;gap:1rem;align-items:flex-start;">'
            f'<div style="width:50px;height:50px;border-radius:12px;background:linear-gradient(135deg,#2563eb,#7c3aed);'
            f'display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:1.1rem;flex-shrink:0;">{initials}</div>'
            f'<div><div style="font-weight:600;font-size:1rem;color:#111827;">{user["username"]}</div>'
            f'<div style="font-size:0.82rem;color:#9ca3af;">{user["email"]}</div>'
            f'<div style="margin-top:5px"><span class="pill-student">Student</span></div>'
            f'<div style="font-size:0.78rem;color:#9ca3af;margin-top:6px;">Member since {user["created_at"][:10]}</div>'
            f'</div></div>', unsafe_allow_html=True
        )

        st.markdown("<br>**Change Password**")
        with st.form("change_pw"):
            cur = st.text_input("Current Password", type="password")
            new_pw = st.text_input("New Password", type="password")
            conf = st.text_input("Confirm New Password", type="password")
            if st.form_submit_button("Update Password", type="primary"):
                if not cur or not new_pw or not conf:
                    st.error("All fields required.")
                elif not auth.verify_password(cur, user['password_hash']):
                    st.error("Current password is incorrect.")
                elif new_pw != conf:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = auth.validate_password(new_pw)
                    if not ok: st.error(msg)
                    else:
                        db.update_user_password(st.session_state.user_id, auth.hash_password(new_pw))
                        st.success("Password updated.")

    with c2:
        stat_card("Total Days", stats['total_days'], style="blue")
        stat_card("Present", stats['present_days'], style="good")
        stat_card("Rate", f"{stats['percentage']}%", style=pct_style(stats['percentage']))


# ─────────────────────────────────────────────────────────
# ADMIN SIDEBAR
# ─────────────────────────────────────────────────────────

def admin_sidebar():
    with st.sidebar:
        initials = st.session_state.username[:2].upper()
        st.markdown(
            f'<div class="sidebar-user">'
            f'<div class="sidebar-avatar" style="background:linear-gradient(135deg,#dc2626,#9f1239);">{initials}</div>'
            f'<div class="sidebar-name">{st.session_state.username}</div>'
            f'<div class="sidebar-email">{st.session_state.email}</div>'
            f'<div style="margin-top:7px"><span class="pill-admin">Administrator</span></div>'
            f'</div>', unsafe_allow_html=True
        )

        st.markdown('<div class="sidebar-section">Admin Panel</div>', unsafe_allow_html=True)
        nav = {
            "admin_home":        "Dashboard",
            "admin_students":    "Students",
            "admin_attendance":  "Attendance Records",
            "admin_mark":        "Mark Attendance",
            "admin_assignments": "Assignments",
            "admin_notices":     "Notices",
            "admin_add_admin":   "Manage Admins",
        }
        for key, label in nav.items():
            t = "primary" if st.session_state.page == key else "secondary"
            if st.button(label, key=f"anav_{key}", use_container_width=True, type=t):
                st.session_state.page = key
                st.rerun()

        st.markdown("---")
        if st.button("Sign Out", key="anav_logout", use_container_width=True):
            auth.logout_user(st.session_state)
            st.rerun()


# ─────────────────────────────────────────────────────────
# ADMIN PAGES
# ─────────────────────────────────────────────────────────

def admin_home():
    page_header("Dashboard", f"Overview — {datetime.now().strftime('%B %d, %Y')}")

    all_users = db.get_all_users()
    students = [u for u in all_users if u['role'] == 'student']
    all_att = db.get_all_attendance()
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_att = [r for r in all_att if r['date'] == today_str]
    today_pct = round(len(today_att) / len(students) * 100, 1) if students else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: stat_card("Total Students", len(students), style="blue")
    with c2: stat_card("Present Today", len(today_att), sub=f"out of {len(students)}", style="good")
    with c3: stat_card("Today's Rate", f"{today_pct}%", style=pct_style(today_pct))
    with c4: stat_card("Assignments", len(db.get_all_assignments()), style="purple")

    # Absent today
    present_ids = {r['user_id'] for r in all_att if r['date'] == today_str}
    absent = [s for s in students if s['id'] not in present_ids]
    if absent:
        st.markdown("---")
        names = ", ".join([s['username'] for s in absent[:12]])
        if len(absent) > 12: names += f" and {len(absent)-12} more"
        st.markdown(f"**Absent Today ({len(absent)})**")
        st.markdown(
            f'<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:10px;'
            f'padding:0.75rem 1rem;font-size:0.86rem;color:#b91c1c;">{names}</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("**Student Attendance Summary**")
    summary = db.get_student_attendance_summary()
    if summary:
        df = pd.DataFrame(summary)[['username', 'email', 'total_days', 'present_days', 'percentage']]
        df.columns = ['Username', 'Email', 'Total Days', 'Present', 'Attendance %']
        def color_pct(val):
            if val >= 75: return 'color:#16a34a;font-weight:600'
            if val >= 50: return 'color:#b45309;font-weight:600'
            return 'color:#dc2626;font-weight:600'
        st.dataframe(df.style.applymap(color_pct, subset=['Attendance %']), use_container_width=True, hide_index=True)
    else:
        st.info("No students registered yet.")


def admin_students():
    page_header("Students", "View and manage registered students")
    students = db.get_student_attendance_summary()
    if not students:
        st.info("No students registered.")
        return

    search = st.text_input("Search", placeholder="Filter by name or email...")
    df = pd.DataFrame(students)
    if search:
        df = df[df['username'].str.contains(search, case=False) | df['email'].str.contains(search, case=False)]

    st.markdown(f"<p style='color:#9ca3af;font-size:0.82rem;'>{len(df)} student(s)</p>", unsafe_allow_html=True)

    for _, row in df.iterrows():
        pct = row['percentage']
        with st.expander(f"{row['username']}  ·  {row['email']}  ·  {pct}%"):
            c1, c2, c3 = st.columns(3)
            with c1: stat_card("Total Days", row['total_days'], style="blue")
            with c2: stat_card("Present", row['present_days'], style="good")
            with c3: stat_card("Rate", f"{pct}%", style=pct_style(pct))
            st.markdown(attendance_bar(pct), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            records = db.get_user_attendance(row['id'])
            if records:
                hist = pd.DataFrame(records)[['date', 'time', 'status', 'marked_by']]
                hist.columns = ['Date', 'Time', 'Status', 'Marked By']
                st.dataframe(hist, use_container_width=True, hide_index=True)
                st.download_button(
                    f"Download {row['username']}'s records", hist.to_csv(index=False),
                    f"{row['username']}_attendance.csv", "text/csv", key=f"sdl_{row['id']}"
                )
            else:
                st.caption("No attendance records yet.")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"Remove {row['username']}", key=f"del_{row['id']}"):
                db.delete_user(row['id'])
                st.warning(f"'{row['username']}' removed.")
                st.rerun()


def admin_all_attendance():
    page_header("Attendance Records", "Complete attendance log")
    records = db.get_all_attendance()
    if not records:
        st.info("No attendance records found.")
        return

    df = pd.DataFrame(records)[['username', 'email', 'date', 'time', 'status', 'marked_by']].rename(
        columns={'username': 'Username', 'email': 'Email', 'date': 'Date',
                 'time': 'Time', 'status': 'Status', 'marked_by': 'Marked By'}
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        user_filter = st.selectbox("Student", ["All"] + sorted(df['Username'].unique().tolist()))
    with c2:
        date_filter = st.date_input("Date", value=None)
    with c3:
        month_filter = st.selectbox("Month", ["All"] + [f"{m:02d}" for m in range(1, 13)])

    if user_filter != "All": df = df[df['Username'] == user_filter]
    if date_filter: df = df[df['Date'] == str(date_filter)]
    if month_filter != "All": df = df[df['Date'].str[5:7] == month_filter]

    st.markdown(f"<p style='color:#9ca3af;font-size:0.82rem;'>{len(df)} record(s)</p>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Download CSV", df.to_csv(index=False), "attendance_export.csv", "text/csv")


def admin_mark_attendance():
    page_header("Mark Attendance", "Record attendance on behalf of a student")
    students = db.get_all_students()
    if not students:
        st.info("No students registered.")
        return

    c1, c2 = st.columns(2)
    with c1:
        selected_name = st.selectbox("Student", [s['username'] for s in students])
    with c2:
        mark_date = st.date_input("Date", value=datetime.now(), max_value=datetime.now())

    selected = next(s for s in students if s['username'] == selected_name)
    if st.button("Mark as Present", type="primary"):
        ok, msg = db.mark_attendance_for_date(selected['id'], str(mark_date), marked_by=st.session_state.username)
        st.success(msg) if ok else st.warning(msg)

    st.markdown("---")
    st.markdown(f"**Recent records — {selected_name}**")
    records = db.get_user_attendance(selected['id'])
    if records:
        df = pd.DataFrame(records)[['date', 'time', 'status', 'marked_by']].head(15)
        df.columns = ['Date', 'Time', 'Status', 'Marked By']
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("No records yet.")


def admin_assignments():
    page_header("Assignments", "Create and manage assignments for students")
    tab1, tab2 = st.tabs(["Upload Assignment", "All Assignments"])

    with tab1:
        with st.form("upload_asgn"):
            title = st.text_input("Title")
            description = st.text_area("Description / Instructions")
            due_date = st.date_input("Due Date", value=None)
            uploaded_file = st.file_uploader("Attach file (optional)")
            submitted = st.form_submit_button("Upload Assignment", type="primary", use_container_width=True)

            if submitted:
                if not title:
                    st.error("Title is required.")
                else:
                    fp = fn = None
                    if uploaded_file:
                        os.makedirs("uploads", exist_ok=True)
                        fp = os.path.join("uploads", uploaded_file.name)
                        with open(fp, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        fn = uploaded_file.name
                    db.add_assignment(title, description, fn, fp,
                                      str(due_date) if due_date else None, st.session_state.username)
                    st.success("Assignment posted.")
                    st.rerun()

    with tab2:
        assignments = db.get_all_assignments()
        if not assignments:
            st.info("No assignments yet.")
        for a in assignments:
            with st.expander(f"{a['title']}  ·  Due: {a['due_date'] or 'N/A'}  ·  {a['created_at'][:10]}"):
                st.markdown(f"**Description:** {a['description'] or '—'}")
                st.caption(f"Posted by {a['uploaded_by']}")
                if a['filepath'] and os.path.exists(a['filepath']):
                    with open(a['filepath'], "rb") as f:
                        st.download_button("Download", f, a['filename'], key=f"adl_{a['id']}")
                if st.button("Delete", key=f"adel_{a['id']}"):
                    db.delete_assignment(a['id'])
                    st.warning("Deleted.")
                    st.rerun()


def admin_notices():
    page_header("Notices", "Post announcements visible to all students")
    tab1, tab2 = st.tabs(["Post Notice", "All Notices"])

    with tab1:
        with st.form("post_notice"):
            title = st.text_input("Title")
            body = st.text_area("Content", height=150)
            submitted = st.form_submit_button("Post Notice", type="primary", use_container_width=True)
            if submitted:
                if not title or not body:
                    st.error("Title and content are required.")
                else:
                    db.add_notice(title, body, st.session_state.username)
                    st.success("Notice posted.")
                    st.rerun()

    with tab2:
        notices = db.get_all_notices()
        if not notices:
            st.info("No notices yet.")
        for n in notices:
            with st.expander(f"{n['title']}  ·  {n['created_at'][:10]}"):
                st.markdown(n['body'])
                st.caption(f"Posted by {n['posted_by']}")
                if st.button("Delete", key=f"ndel_{n['id']}"):
                    db.delete_notice(n['id'])
                    st.warning("Deleted.")
                    st.rerun()


def admin_add_admin():
    page_header("Manage Admins", "Create additional administrator accounts")
    st.info("Admin accounts cannot be created through the public registration page.")

    with st.form("add_admin"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Create Admin Account", type="primary", use_container_width=True)
        if submitted:
            if not username or not email or not password or not confirm:
                st.error("All fields required.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                ok, msg = auth.signup_user(username, email, password, role="admin")
                st.success(f"Admin '{username}' created.") if ok else st.error(msg)

    st.markdown("---")
    st.markdown("**Current Administrators**")
    admins = [u for u in db.get_all_users() if u['role'] == 'admin']
    if admins:
        df = pd.DataFrame(admins)[['username', 'email', 'created_at']].rename(
            columns={'username': 'Username', 'email': 'Email', 'created_at': 'Created'}
        )
        st.dataframe(df, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────
# ROUTERS + MAIN
# ─────────────────────────────────────────────────────────

def route_student():
    student_sidebar()
    p = st.session_state.page
    if p == "mark": student_mark_attendance()
    elif p == "view": student_view_attendance()
    elif p == "assignments": student_assignments()
    elif p == "notices": student_notices()
    elif p == "profile": student_profile()
    else: student_dashboard()


def route_admin():
    admin_sidebar()
    p = st.session_state.page
    if p == "admin_students": admin_students()
    elif p == "admin_attendance": admin_all_attendance()
    elif p == "admin_mark": admin_mark_attendance()
    elif p == "admin_assignments": admin_assignments()
    elif p == "admin_notices": admin_notices()
    elif p == "admin_add_admin": admin_add_admin()
    else: admin_home()


def main():
    db.init_database()
    init_session_state()

    # ✅ DOCKER VERSION INDICATOR (VISIBLE AFTER LOGIN)
    if st.session_state.authenticated:
        st.success("New Version Running 🚀")

    if not st.session_state.authenticated:
        signup_page() if st.session_state.page == 'signup' else login_page()
        return

    if st.session_state.role == "admin":
        if st.session_state.page == "dashboard":
            st.session_state.page = "admin_home"
        route_admin()
    else:
        if st.session_state.page not in ("dashboard", "mark", "view", "assignments", "notices", "profile"):
            st.session_state.page = "dashboard"
        route_student()


if __name__ == "__main__":
    main()

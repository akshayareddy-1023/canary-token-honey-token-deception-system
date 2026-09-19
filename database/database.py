import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_FILE = os.path.join(BASE_DIR, "database", "events.db")


def create_database():
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)

    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_id TEXT NOT NULL,
            triggered_at TEXT NOT NULL,
            ip_address TEXT,
            request_method TEXT,
            status TEXT DEFAULT 'TRIGGERED'
        )
    """)

    existing = {
        row[1] for row in cursor.execute("PRAGMA table_info(events)").fetchall()
    }

    new_columns = {
        "user_agent": "TEXT",
        "alert_type": "TEXT",
        "severity": "TEXT",
        "message": "TEXT",
        "location": "TEXT"
    }

    for column_name, column_type in new_columns.items():
        if column_name not in existing:
            cursor.execute(
                f"ALTER TABLE events ADD COLUMN {column_name} {column_type}"
            )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocked_ips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT UNIQUE NOT NULL,
            blocked_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_event(
    token_id,
    triggered_at,
    ip_address,
    request_method,
    user_agent="Unknown",
    alert_type="HONEY_TOKEN_TRIGGERED",
    severity="HIGH",
    message="",
    location="Unknown"
):
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO events
        (token_id, triggered_at, ip_address, request_method, status,
         user_agent, alert_type, severity, message, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        token_id, triggered_at, ip_address, request_method, "TRIGGERED",
        user_agent, alert_type, severity, message, location
    ))

    connection.commit()
    connection.close()


def get_all_events():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM events ORDER BY id DESC")
    events = cursor.fetchall()

    connection.close()
    return events


def get_dashboard_stats():
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    total_tokens = cursor.execute(
        "SELECT COUNT(DISTINCT token_id) FROM events"
    ).fetchone()[0]

    total_incidents = cursor.execute(
        "SELECT COUNT(*) FROM events"
    ).fetchone()[0]

    high_alerts = cursor.execute("""
        SELECT COUNT(*) FROM events
        WHERE severity = 'HIGH' OR status = 'TRIGGERED'
    """).fetchone()[0]

    unique_ips = cursor.execute("""
        SELECT COUNT(DISTINCT ip_address) FROM events
        WHERE ip_address IS NOT NULL
    """).fetchone()[0]

    blocked_ips = cursor.execute(
        "SELECT COUNT(*) FROM blocked_ips"
    ).fetchone()[0]

    connection.close()

    return {
        "total_tokens": total_tokens,
        "total_incidents": total_incidents,
        "high_alerts": high_alerts,
        "unique_ips": unique_ips,
        "blocked_ips": blocked_ips
    }


def block_ip(ip_address, blocked_at):
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO blocked_ips (ip_address, blocked_at)
        VALUES (?, ?)
    """, (ip_address, blocked_at))

    connection.commit()
    connection.close()


def unblock_ip(ip_address):
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM blocked_ips WHERE ip_address = ?", (ip_address,))
    connection.commit()
    connection.close()


def is_ip_blocked(ip_address):
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()
    row = cursor.execute(
        "SELECT 1 FROM blocked_ips WHERE ip_address = ? LIMIT 1",
        (ip_address,)
    ).fetchone()
    connection.close()
    return row is not None


def get_blocked_ips():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    rows = cursor.execute(
        "SELECT * FROM blocked_ips ORDER BY id DESC"
    ).fetchall()
    connection.close()
    return rows

import sqlite3
import os


# =========================================================
# DATABASE PATH
# =========================================================

DATABASE_FILE = os.path.join(
    os.path.dirname(__file__),
    "events.db"
)


# =========================================================
# CREATE / UPDATE DATABASE
# =========================================================

def create_database():

    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    # -----------------------------------------------------
    # Create events table if it does not exist
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_id TEXT NOT NULL,
            triggered_at TEXT NOT NULL,
            ip_address TEXT,
            request_method TEXT,
            status TEXT,
            user_agent TEXT,
            alert_type TEXT,
            severity TEXT,
            message TEXT
        )
    """)

    # -----------------------------------------------------
    # Check existing columns
    # -----------------------------------------------------

    cursor.execute("PRAGMA table_info(events)")
    existing_columns = [
        column[1]
        for column in cursor.fetchall()
    ]

    # -----------------------------------------------------
    # Add missing columns to an existing database
    # -----------------------------------------------------

    new_columns = {
        "user_agent": "TEXT",
        "alert_type": "TEXT",
        "severity": "TEXT",
        "message": "TEXT"
    }

    for column_name, column_type in new_columns.items():

        if column_name not in existing_columns:

            cursor.execute(
                f"""
                ALTER TABLE events
                ADD COLUMN {column_name} {column_type}
                """
            )

    connection.commit()
    connection.close()


# =========================================================
# SAVE SECURITY EVENT
# =========================================================

def save_event(
    token_id,
    triggered_at,
    ip_address,
    request_method,
    user_agent="Unknown",
    alert_type="HONEY_TOKEN_TRIGGERED",
    severity="HIGH",
    message=""
):

    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO events
        (
            token_id,
            triggered_at,
            ip_address,
            request_method,
            status,
            user_agent,
            alert_type,
            severity,
            message
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        token_id,
        triggered_at,
        ip_address,
        request_method,
        "TRIGGERED",
        user_agent,
        alert_type,
        severity,
        message
    ))

    connection.commit()
    connection.close()


# =========================================================
# GET ALL EVENTS
# =========================================================

def get_all_events():

    connection = sqlite3.connect(DATABASE_FILE)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM events
        ORDER BY id DESC
    """)

    events = cursor.fetchall()

    connection.close()

    return events


# =========================================================
# GET DASHBOARD STATISTICS
# =========================================================

def get_dashboard_stats():

    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    # -----------------------------------------------------
    # Total unique honey tokens triggered
    # -----------------------------------------------------

    cursor.execute(
        "SELECT COUNT(DISTINCT token_id) FROM events"
    )

    total_tokens = cursor.fetchone()[0]

    # -----------------------------------------------------
    # Total incidents
    # -----------------------------------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM events"
    )

    total_incidents = cursor.fetchone()[0]

    # -----------------------------------------------------
    # High severity alerts
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM events
        WHERE severity = 'HIGH'
           OR status = 'TRIGGERED'
    """)

    high_alerts = cursor.fetchone()[0]

    # -----------------------------------------------------
    # Unique IP addresses
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COUNT(DISTINCT ip_address)
        FROM events
        WHERE ip_address IS NOT NULL
    """)

    unique_ips = cursor.fetchone()[0]

    connection.close()

    return {
        "total_tokens": total_tokens,
        "total_incidents": total_incidents,
        "high_alerts": high_alerts,
        "unique_ips": unique_ips
    }


# =========================================================
# TEST DATABASE
# =========================================================

if __name__ == "__main__":

    create_database()

    print("Database created/updated successfully.")
    print("Database location:")
    print(DATABASE_FILE)
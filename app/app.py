from flask import Flask, jsonify, render_template

import json
import os


# =========================================================
# DATABASE
# =========================================================

from database.database import (
    create_database,
    save_event,
    get_all_events,
    get_dashboard_stats
)


# =========================================================
# DETECTION
# =========================================================

from detection.detector import (
    create_detection_event,
    print_detection_alert
)


# =========================================================
# ALERT MANAGER
# =========================================================

from alerts.alert_manager import generate_alert


# =========================================================
# HONEY TOKEN GENERATOR
# =========================================================

from honeytokens.generator import generate_honey_token


# =========================================================
# FILE HONEY TOKEN
# =========================================================

from honeytokens.file_honeytoken import generate_file_honeytoken


# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(
    __name__,
    template_folder=os.path.join(
        BASE_DIR,
        "templates"
    ),
    static_folder=os.path.join(
        BASE_DIR,
        "static"
    )
)


# =========================================================
# TOKEN FILE
# =========================================================

TOKEN_FILE = os.path.join(
    BASE_DIR,
    "honeytokens",
    "tokens.json"
)


# =========================================================
# CREATE DATABASE
# =========================================================

create_database()


# =========================================================
# LOAD TOKENS
# =========================================================

def load_tokens():

    if not os.path.exists(TOKEN_FILE):
        return []

    try:

        with open(
            TOKEN_FILE,
            "r"
        ) as file:

            return json.load(file)

    except (
        json.JSONDecodeError,
        FileNotFoundError
    ):

        return []


# =========================================================
# SAVE TOKENS
# =========================================================

def save_tokens(tokens):

    with open(
        TOKEN_FILE,
        "w"
    ) as file:

        json.dump(
            tokens,
            file,
            indent=4
        )


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return """
    <h1>Canary Token Active Honey Token Deception System</h1>

    <p>System is running successfully.</p>

    <p>
        <a href="/dashboard">
            Open Security Dashboard
        </a>
    </p>

    <p>
        <a href="/generate-token">
            Generate URL Honey Token
        </a>
    </p>

    <p>
        <a href="/generate-file-token">
            Generate File Honey Token
        </a>
    </p>
    """


# =========================================================
# GENERATE NEW HONEY TOKEN
# =========================================================

@app.route("/generate-token")
def generate_token():

    token = generate_honey_token()

    trigger_url = (
        f"/honeytoken/{token['token_id']}"
    )

    return jsonify({

        "message":
            "New Honey Token Generated Successfully",

        "token":
            token,

        "trigger_url":
            trigger_url
    })


# =========================================================
# GENERATE FILE HONEY TOKEN
# =========================================================

@app.route("/generate-file-token")
def generate_file_token():

    token = generate_file_honeytoken(
        "Confidential_Report.txt"
    )

    trigger_url = (
        f"/honeytoken/{token['token_id']}"
    )

    return jsonify({

        "message":
            "File Honey Token Generated Successfully",

        "token":
            token,

        "trigger_url":
            trigger_url
    })


# =========================================================
# HONEY TOKEN TRIGGER
# =========================================================

@app.route("/honeytoken/<token_id>")
def trigger_honeytoken(token_id):

    print("\n")

    print("=" * 60)

    print("HONEY TOKEN ROUTE ACCESSED")

    print("Token ID:", token_id)

    print("=" * 60)


    # -----------------------------------------------------
    # Load all tokens
    # -----------------------------------------------------

    tokens = load_tokens()


    # -----------------------------------------------------
    # Search for requested token
    # -----------------------------------------------------

    for token in tokens:

        if token["token_id"] == token_id:

            # -------------------------------------------------
            # CHANGE TOKEN STATUS
            # -------------------------------------------------

            token["status"] = "TRIGGERED"

            save_tokens(tokens)

            print(
                "Token status changed to TRIGGERED"
            )


            # -------------------------------------------------
            # CREATE DETECTION EVENT
            # -------------------------------------------------

            event = create_detection_event(
                token_id
            )


            # -------------------------------------------------
            # PRINT DETECTION ALERT
            # -------------------------------------------------

            print_detection_alert(
                event
            )


            # -------------------------------------------------
            # GENERATE SECURITY ALERT
            # -------------------------------------------------

            alert = generate_alert(
                event
            )


            # -------------------------------------------------
            # SAVE COMPLETE EVENT + ALERT DETAILS
            # -------------------------------------------------

            save_event(

                event["token_id"],

                event["triggered_at"],

                event["ip_address"],

                event["request_method"],

                event.get(
                    "user_agent",
                    "Unknown"
                ),

                alert.get(
                    "alert_type",
                    "HONEY_TOKEN_TRIGGERED"
                ),

                alert.get(
                    "severity",
                    "HIGH"
                ),

                alert.get(
                    "message",
                    ""
                )
            )


            print(
                "\nAlert details saved to database."
            )


            # -------------------------------------------------
            # RESPONSE
            # -------------------------------------------------

            return jsonify({

                "message":
                    "Honey Token Triggered",

                "event":
                    event,

                "alert":
                    alert

            })


    # =====================================================
    # INVALID TOKEN
    # =====================================================

    print(
        "Invalid Honey Token"
    )

    return jsonify({

        "message":
            "Invalid Honey Token"

    }), 404


# =========================================================
# SECURITY DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    # -----------------------------------------------------
    # Get database events
    # -----------------------------------------------------

    events = get_all_events()


    # -----------------------------------------------------
    # Get database statistics
    # -----------------------------------------------------

    stats = get_dashboard_stats()


    # -----------------------------------------------------
    # Load tokens
    # -----------------------------------------------------

    tokens = load_tokens()


    # -----------------------------------------------------
    # Token statistics
    # -----------------------------------------------------

    total_tokens = len(tokens)


    active_tokens = sum(

        1

        for token in tokens

        if token.get("status") == "ACTIVE"

    )


    triggered_tokens = sum(

        1

        for token in tokens

        if token.get("status") == "TRIGGERED"

    )


    # -----------------------------------------------------
    # Incident statistics
    # -----------------------------------------------------

    total_incidents = (
        stats["total_incidents"]
    )


    high_alerts = (
        stats["high_alerts"]
    )


    unique_ips = (
        stats["unique_ips"]
    )


    # -----------------------------------------------------
    # Incident rate
    # -----------------------------------------------------

    if total_tokens > 0:

        incident_rate = round(

            (
                triggered_tokens
                /
                total_tokens
            )
            * 100,

            1

        )

    else:

        incident_rate = 0


    # -----------------------------------------------------
    # Incident count by token
    # -----------------------------------------------------

    incident_counts = {}


    for event in events:

        token_id = event["token_id"]


        if token_id in incident_counts:

            incident_counts[token_id] += 1

        else:

            incident_counts[token_id] = 1


    incident_labels = list(
        incident_counts.keys()
    )


    incident_values = list(
        incident_counts.values()
    )


    # -----------------------------------------------------
    # Render dashboard
    # -----------------------------------------------------

    return render_template(

        "dashboard.html",

        events=events,

        tokens=tokens,

        total_tokens=total_tokens,

        total_incidents=total_incidents,

        high_alerts=high_alerts,

        unique_ips=unique_ips,

        active_tokens=active_tokens,

        triggered_tokens=triggered_tokens,

        incident_rate=incident_rate,

        incident_labels=incident_labels,

        incident_values=incident_values

    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
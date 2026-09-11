from datetime import datetime
from flask import request


def create_detection_event(token_id):
    """
    Create an event containing information about
    the request that triggered a honey token.
    """

    event = {
        "token_id": token_id,
        "triggered_at": datetime.now().isoformat(),
        "ip_address": request.remote_addr,
        "request_method": request.method,
        "user_agent": request.headers.get("User-Agent", "Unknown"),
        "status": "TRIGGERED"
    }

    return event


def print_detection_alert(event):
    """
    Display the detected honey-token access
    in the application terminal.
    """

    print("\n" + "=" * 50)
    print("🚨 HONEY TOKEN ACCESS DETECTED 🚨")
    print("=" * 50)

    print("Token ID      :", event["token_id"])
    print("Triggered At  :", event["triggered_at"])
    print("IP Address    :", event["ip_address"])
    print("Request Method:", event["request_method"])
    print("User Agent    :", event["user_agent"])
    print("Status        :", event["status"])

    print("=" * 50)
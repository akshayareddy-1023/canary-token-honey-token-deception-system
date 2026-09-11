def generate_alert(event):
    """
    Generate a security alert for a triggered honey token.
    """

    alert = {
        "alert_type": "HONEY_TOKEN_TRIGGERED",
        "severity": "HIGH",
        "message": (
            f"Honey token {event['token_id']} "
            f"was accessed from IP {event['ip_address']}"
        ),
        "triggered_at": event["triggered_at"]
    }

    print("\n🚨 SECURITY ALERT 🚨")
    print("Alert Type :", alert["alert_type"])
    print("Severity   :", alert["severity"])
    print("Message    :", alert["message"])
    print("Time       :", alert["triggered_at"])

    return alert
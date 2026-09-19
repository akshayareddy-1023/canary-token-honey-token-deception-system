import json
import os
import secrets
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "database", "admin_config.json")
DEFAULT_USERNAME = os.environ.get("CANARY_ADMIN_USERNAME", "admin")


def _load():
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def ensure_admin():
    """Create the local admin account on first run without storing a plaintext password in source code."""
    if _load():
        return None

    initial_password = os.environ.get("CANARY_ADMIN_PASSWORD") or secrets.token_urlsafe(12)
    data = {
        "username": DEFAULT_USERNAME,
        "password_hash": generate_password_hash(initial_password),
        "created_at": datetime.now().isoformat(),
        "password_changed": False,
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("\n=== Initial CanaryShield Admin Account ===")
    print(f"Username: {DEFAULT_USERNAME}")
    print(f"Password: {initial_password}")
    print("Change this password from the Admin Dashboard after signing in.")
    print("===========================================\n")
    return initial_password


def verify_credentials(username, password):
    ensure_admin()
    data = _load()
    return bool(
        data
        and username == data.get("username")
        and check_password_hash(data.get("password_hash", ""), password)
    )


def change_password(current_password, new_password):
    ensure_admin()
    data = _load()
    if not check_password_hash(data.get("password_hash", ""), current_password):
        return False, "Current password is incorrect."
    if len(new_password) < 8:
        return False, "New password must contain at least 8 characters."
    data["password_hash"] = generate_password_hash(new_password)
    data["password_changed"] = True
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return True, "Administrator password changed successfully."


def username():
    ensure_admin()
    return (_load() or {}).get("username", DEFAULT_USERNAME)

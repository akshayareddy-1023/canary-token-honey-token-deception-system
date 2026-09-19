import secrets
import json
import os
import re
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "tokens.json")
DECOY_FOLDER = os.path.join(BASE_DIR, "decoy_files")

os.makedirs(DECOY_FOLDER, exist_ok=True)


def _load_tokens():
    if not os.path.exists(TOKEN_FILE):
        return []
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save_tokens(tokens):
    with open(TOKEN_FILE, "w", encoding="utf-8") as file:
        json.dump(tokens, file, indent=4)


def _make_unique_filename(filename, tokens):
    """Return a safe, unique decoy filename.

    The admin can choose the base name. If that name already exists, a
    numbered suffix is added so every generated honeytoken has its own file.
    """
    filename = os.path.basename(filename).strip()
    if not filename:
        filename = "Confidential_Report.txt"

    # Remove characters that are unsafe or awkward in Windows filenames.
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.rstrip('. ')

    stem, extension = os.path.splitext(filename)
    if not extension:
        extension = ".txt"

    existing = {str(t.get("filename", "")).lower() for t in tokens}
    candidate = f"{stem}{extension}"
    number = 1

    while candidate.lower() in existing or os.path.exists(os.path.join(DECOY_FOLDER, candidate)):
        candidate = f"{stem}_{number:03d}{extension}"
        number += 1

    return candidate


def generate_file_honeytoken(filename="Confidential_Report.txt"):
    # Keep generated files inside the decoy folder and make every name unique.
    tokens = _load_tokens()
    filename = _make_unique_filename(filename, tokens)
    token_id = secrets.token_hex(16)

    token = {
        "token_id": token_id,
        "token_type": "FILE",
        "filename": filename,
        "created_at": datetime.now().isoformat(),
        "status": "ACTIVE"
    }

    tokens.append(token)
    _save_tokens(tokens)

    file_path = os.path.join(DECOY_FOLDER, filename)

    # The unique token URL is generated from this file's token ID.
    trigger_url = f"/honeytoken/{token_id}"

    file_content = f"""============================================================
CONFIDENTIAL COMPANY REPORT
============================================================

Document Classification:
CONFIDENTIAL

Document ID:
{token_id}

Report:
Internal Security and Operations Report

This document contains confidential information
intended only for authorized personnel.

------------------------------------------------------------
SECURITY VERIFICATION
------------------------------------------------------------

Security Verification:
{trigger_url}

------------------------------------------------------------
WARNING
------------------------------------------------------------

Unauthorized access to this document may be monitored
and recorded by the organization's security system.

============================================================
"""

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(file_content)

    token["file_path"] = file_path
    token["trigger_url"] = trigger_url
    return token

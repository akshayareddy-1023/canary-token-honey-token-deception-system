import secrets
import json
import os
from datetime import datetime


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

TOKEN_FILE = os.path.join(
    os.path.dirname(__file__),
    "tokens.json"
)

DECOY_FOLDER = os.path.join(
    BASE_DIR,
    "decoy_files"
)


# =========================================================
# CREATE DECOY FOLDER
# =========================================================

os.makedirs(
    DECOY_FOLDER,
    exist_ok=True
)


# =========================================================
# GENERATE FILE HONEY TOKEN
# =========================================================

def generate_file_honeytoken(
    filename="Confidential_Report.txt"
):

    # -----------------------------------------------------
    # Generate unique token
    # -----------------------------------------------------

    token_id = secrets.token_hex(16)


    # -----------------------------------------------------
    # Create trigger URL
    # -----------------------------------------------------

    trigger_url = (
        f"http://127.0.0.1:5000/honeytoken/{token_id}"
    )


    # -----------------------------------------------------
    # Token information
    # -----------------------------------------------------

    token = {

        "token_id":
            token_id,

        "token_type":
            "FILE",

        "filename":
            filename,

        "created_at":
            datetime.now().isoformat(),

        "status":
            "ACTIVE"

    }


    # -----------------------------------------------------
    # Load existing tokens
    # -----------------------------------------------------

    if os.path.exists(TOKEN_FILE):

        try:

            with open(
                TOKEN_FILE,
                "r"
            ) as file:

                tokens = json.load(file)

        except json.JSONDecodeError:

            tokens = []

    else:

        tokens = []


    # -----------------------------------------------------
    # Add new token
    # -----------------------------------------------------

    tokens.append(token)


    # -----------------------------------------------------
    # Save token
    # -----------------------------------------------------

    with open(
        TOKEN_FILE,
        "w"
    ) as file:

        json.dump(
            tokens,
            file,
            indent=4
        )


    # =====================================================
    # CREATE DECOY FILE
    # =====================================================

    file_path = os.path.join(
        DECOY_FOLDER,
        filename
    )


    # -----------------------------------------------------
    # File content
    # -----------------------------------------------------

    file_content = f"""
============================================================
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

If you received this document unexpectedly, verify
your authorization before accessing the security
verification link below.

Security Verification:
{trigger_url}

------------------------------------------------------------
WARNING
------------------------------------------------------------

Unauthorized access to this document may be monitored
and recorded by the organization's security system.

============================================================
"""


    # -----------------------------------------------------
    # Write decoy file
    # -----------------------------------------------------

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            file_content
        )


    # -----------------------------------------------------
    # Add file information to response
    # -----------------------------------------------------

    token["file_path"] = file_path

    token["trigger_url"] = trigger_url


    return token
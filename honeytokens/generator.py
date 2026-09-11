import secrets
import json
import os
from datetime import datetime


TOKEN_FILE = os.path.join(
    os.path.dirname(__file__),
    "tokens.json"
)


def generate_honey_token():
    token_id = secrets.token_hex(16)

    token = {
        "token_id": token_id,
        "created_at": datetime.now().isoformat(),
        "status": "ACTIVE"
    }

    # Load existing tokens
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as file:
            tokens = json.load(file)
    else:
        tokens = []

    # Add new token
    tokens.append(token)

    # Save tokens
    with open(TOKEN_FILE, "w") as file:
        json.dump(tokens, file, indent=4)

    return token


if __name__ == "__main__":
    token = generate_honey_token()

    print("Honey Token Created")
    print("-------------------")
    print("Token ID:", token["token_id"])
    print("Created At:", token["created_at"])
    print("Status:", token["status"])
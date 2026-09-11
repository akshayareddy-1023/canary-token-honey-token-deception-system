# Canary Token Active Honey Token Deception System

A Flask-based cybersecurity deception system that uses **honey tokens and decoy files** to detect unauthorized access attempts. The application generates unique tokens, monitors token access, records security events, creates high-severity alerts, and presents the activity through a web-based security dashboard.

## Why this project?

Traditional security monitoring can miss suspicious activity that occurs after an attacker has already gained access to a system. A honey token is a deliberately placed digital resource that should not be accessed during normal operation. If it is triggered, the event can be treated as a strong indicator of suspicious activity.

This project demonstrates that concept in a simple, practical web application suitable for learning and academic cybersecurity projects.

## Key Features

- **URL Honey Token Generation** – creates unique cryptographically random token IDs.
- **File Honey Tokens** – creates a decoy confidential document containing a token-trigger link.
- **Access Detection** – detects when a registered honey token is accessed.
- **Security Alerts** – generates a HIGH-severity alert for a triggered token.
- **Event Logging** – stores token ID, timestamp, IP address, request method, user agent, status, and alert details.
- **SQLite Database** – maintains security-event records locally.
- **Security Dashboard** – displays token status, incidents, alerts, unique IPs, and token history.
- **Incident Statistics** – calculates triggered-token and incident information for monitoring.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and token generation |
| Flask | Web application and REST-style endpoints |
| SQLite | Security-event storage |
| HTML/CSS | Dashboard interface |
| JavaScript | Dashboard interactions and visualizations |
| Chart.js | Dashboard charts |

## Project Architecture

```text
                         +----------------------+
                         |   Flask Web App      |
                         |       app.py         |
                         +----------+-----------+
                                    |
              +---------------------+----------------------+
              |                     |                      |
              v                     v                      v
      +---------------+     +---------------+      +---------------+
      | Honey Tokens  |     |   Detection   |      | Alert Manager |
      |   Generator   |     |    Module     |      |               |
      +-------+-------+     +-------+-------+      +-------+-------+
              |                     |                      |
              |                     +----------+-----------+
              |                                |
              v                                v
      +---------------+                 +---------------+
      | Decoy Files   |                 | SQLite DB     |
      +---------------+                 |  events.db   |
                                        +-------+-------+
                                                |
                                                v
                                      +-------------------+
                                      | Security Dashboard|
                                      +-------------------+
```

## Project Structure

```text
canary-token-honey-token-deception-system/
│
├── alerts/
│   └── alert_manager.py
│
├── app/
│   ├── __init__.py
│   └── app.py
│
├── database/
│   ├── __init__.py
│   └── database.py
│
├── decoy_files/
│   └── # Generated decoy files appear here at runtime
│
├── detection/
│   └── detector.py
│
├── honeytokens/
│   ├── file_honeytoken.py
│   ├── generator.py
│   └── tokens.json.example
│
├── screenshots/
│   ├── dashboard.png
│   ├── token_generation.png
│   ├── alert_trigger.png
│   ├── latest_alert_details.png
│   └── recent_token_history.png
│
├── static/
│   └── style.css
│
├── templates/
│   └── dashboard.html
│
├── tests/
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## How the System Works

First, the application generates a unique honey token using Python's `secrets` module. The token is stored with its creation time and ACTIVE status. A file honey token can also create a decoy document that contains a unique token-trigger URL.

When someone accesses a valid token URL, the Flask application identifies the token and changes its status to TRIGGERED. The detection module collects request information such as the timestamp, source IP address, HTTP method, and user-agent string. The alert manager then creates a HIGH-severity security alert, and the complete event is stored in the SQLite database.

The dashboard reads the stored information and presents token counts, incidents, alerts, unique IP addresses, token history, and other monitoring information in one place.

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/canary-token-honey-token-deception-system.git
cd canary-token-honey-token-deception-system
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m app.app
```

The application starts locally using Flask's development server.

Open the dashboard at:

```text
http://127.0.0.1:5000/dashboard
```

## Main Endpoints

| Endpoint | Purpose |
|---|---|
| `/` | Displays the application home page |
| `/dashboard` | Opens the security monitoring dashboard |
| `/generate-token` | Generates a URL honey token |
| `/generate-file-token` | Generates a file honey token and decoy file |
| `/honeytoken/<token_id>` | Trigger endpoint used to detect token access |

## Screenshots

### Security Dashboard

![Security Dashboard](screenshots/dashboard.png)

### Honey Token Generation

![Honey Token Generation](screenshots/token_generation.png)

### Token Trigger / Detection

![Alert Trigger](screenshots/alert_trigger.png)

### Latest Alert Details

![Latest Alert Details](screenshots/latest_alert_details.png)

### Recent Token History

![Recent Token History](screenshots/recent_token_history.png)

## Security and Privacy Notes

This project is intended for **local development, demonstrations, and academic learning**. Do not deploy it publicly without reviewing authentication, authorization, input validation, logging, secret management, production server configuration, and other security controls.

Generated runtime data such as the SQLite database and token history is intentionally excluded from version control. The repository contains source code and example configuration rather than a developer's local runtime state.

## Future Enhancements

- Email or messaging notifications for triggered tokens
- Authentication and role-based dashboard access
- Additional honey-token types
- Configurable alert severity and rules
- Exportable security reports
- Improved automated testing
- Production-ready deployment configuration

## Academic Project

This repository contains the implementation of a **PBL (Project-Based Learning) cybersecurity project** demonstrating deception-based detection using honey tokens.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

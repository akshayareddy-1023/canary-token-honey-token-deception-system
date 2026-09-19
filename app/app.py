from flask import Flask, jsonify, render_template, request, abort, redirect, url_for, session, flash
from datetime import datetime
from functools import wraps
import json
import os
import secrets
import socket
import urllib.request
import urllib.error
import ipaddress

from database.database import (
    create_database, save_event, get_all_events, get_dashboard_stats,
    block_ip, unblock_ip, is_ip_blocked, get_blocked_ips
)
from database.admin_auth import ensure_admin, verify_credentials, change_password, username
from detection.detector import create_detection_event, print_detection_alert
from alerts.alert_manager import generate_alert
from honeytokens.generator import generate_honey_token
from honeytokens.file_honeytoken import generate_file_honeytoken

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(BASE_DIR, "honeytokens", "tokens.json")
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"), static_folder=os.path.join(BASE_DIR, "static"))
app.secret_key = os.environ.get("CANARY_SECRET_KEY") or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
create_database()
ensure_admin()


def load_tokens():
    if not os.path.exists(TOKEN_FILE): return []
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError): return []


def save_tokens(tokens):
    with open(TOKEN_FILE, "w", encoding="utf-8") as f: json.dump(tokens, f, indent=4)


def system_lan_ip():
    """Return this computer's active LAN address without relying on a hard-coded IP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return "127.0.0.1"
    finally:
        sock.close()


def get_client_ip():
    remote = request.remote_addr or "Unknown"
    # When the same computer accesses its own Flask server, request.remote_addr
    # is loopback. Replace it with the machine's active LAN IP for a useful demo.
    if remote in {"127.0.0.1", "::1"}:
        return system_lan_ip()
    return remote


def lookup_location(ip_address):
    try:
        ip = ipaddress.ip_address(ip_address)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return "Private / Local Network"
    except ValueError:
        return "Unknown"
    try:
        req = urllib.request.Request(f"https://ipwho.is/{ip_address}", headers={"User-Agent":"CanaryToken-PBL/1.0"})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode("utf-8"))
        if data.get("success"):
            return ", ".join([x for x in [data.get("city"), data.get("region"), data.get("country")] if x]) or "Unknown"
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        pass
    return "Location unavailable"


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_authenticated"):
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "message": "Admin authentication required."}), 401
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def build_dashboard_payload():
    events = get_all_events(); stats = get_dashboard_stats(); tokens = load_tokens()
    active = sum(1 for t in tokens if t.get("status") == "ACTIVE")
    triggered = sum(1 for t in tokens if t.get("status") == "TRIGGERED")
    blocked = [dict(r) for r in get_blocked_ips()]
    token_map = {t.get("token_id"): t for t in tokens}
    serial = []
    for e in events:
        row = dict(e); t = token_map.get(row.get("token_id"), {})
        row["resource_name"] = t.get("filename") or t.get("token_id") or "Unknown resource"
        row["token_type"] = t.get("token_type", "URL")
        row["trigger_url"] = t.get("trigger_url", f"/honeytoken/{t.get('token_id','')}")
        serial.append(row)
    labels = [r["resource_name"] for r in serial]
    counts = {}
    for r in serial: counts[r["resource_name"]] = counts.get(r["resource_name"], 0) + 1
    resources = []
    for t in reversed(tokens):
        resources.append({
            "token_id": t.get("token_id"), "filename": t.get("filename") or t.get("token_id"),
            "token_type": t.get("token_type", "URL"), "created_at": t.get("created_at"),
            "status": t.get("status", "ACTIVE"), "trigger_url": t.get("trigger_url") or f"/honeytoken/{t.get('token_id')}"
        })
    return {"stats": {"total_tokens":len(tokens), "active_tokens":active, "triggered_tokens":triggered,
                       "total_incidents":stats["total_incidents"], "high_alerts":stats["high_alerts"],
                       "unique_ips":stats["unique_ips"], "blocked_ips":stats["blocked_ips"]},
            "events":serial, "resources":resources, "blocked_ips":blocked,
            "incident_labels":list(counts.keys()), "incident_values":list(counts.values())}


@app.route("/")
def home(): return redirect(url_for("user_dashboard"))


@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if session.get("admin_authenticated"): return redirect(url_for("dashboard"))
    if request.method == "POST":
        if verify_credentials(request.form.get("username", "").strip(), request.form.get("password", "")):
            session["admin_authenticated"] = True; session["admin_username"] = username()
            return redirect(request.args.get("next") or url_for("dashboard"))
        flash("Invalid administrator credentials.", "error")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.clear(); return redirect(url_for("admin_login"))


@app.route("/admin/change-password", methods=["POST"])
@admin_required
def admin_change_password():
    ok, message = change_password(request.form.get("current_password", ""), request.form.get("new_password", ""))
    flash(message, "success" if ok else "error")
    return redirect(url_for("dashboard"))


@app.route("/user-dashboard")
def user_dashboard():
    tokens = [t for t in load_tokens() if t.get("token_type") == "FILE"]
    return render_template("user_dashboard.html", tokens=tokens)


@app.route("/generate-token")
@admin_required
def generate_token():
    token = generate_honey_token()
    return jsonify({"message":"New Honey Token Generated Successfully", "token":token,
                    "trigger_url":f"/honeytoken/{token['token_id']}"})


@app.route("/generate-file-token")
@admin_required
def generate_file_token():
    filename = request.args.get("filename", "Confidential_Report.txt").strip()
    token = generate_file_honeytoken(filename or "Confidential_Report.txt")
    return jsonify({"message":"File Honey Token Generated Successfully", "token":token,
                    "trigger_url":f"/honeytoken/{token['token_id']}"})


@app.route("/user/file/<token_id>")
def user_open_file(token_id):
    token = next((x for x in load_tokens() if x.get("token_id")==token_id and x.get("token_type")=="FILE"), None)
    if not token: abort(404)
    result = trigger_token(token_id, return_json=False)
    return render_template("file_accessed.html", filename=token.get("filename","Protected File"), blocked=result=="BLOCKED")


def trigger_token(token_id, return_json=True):
    tokens = load_tokens()
    for token in tokens:
        if token.get("token_id") != token_id: continue
        ip = get_client_ip()
        if is_ip_blocked(ip):
            payload={"message":"Request blocked by administrator","ip_address":ip,"status":"BLOCKED"}
            return (jsonify(payload),403) if return_json else "BLOCKED"
        token["status"]="TRIGGERED"; save_tokens(tokens)
        event=create_detection_event(token_id); event["ip_address"]=ip
        location=lookup_location(ip); alert=generate_alert(event)
        save_event(event["token_id"], event["triggered_at"], ip, event["request_method"], event.get("user_agent","Unknown"),
                   alert.get("alert_type","HONEY_TOKEN_TRIGGERED"), alert.get("severity","HIGH"), alert.get("message",""), location)
        print_detection_alert(event); print("Source IP:", ip); print("Location:", location)
        payload={"message":"Honey Token Triggered","event":event,"alert":alert,"location":location}
        return jsonify(payload) if return_json else "TRIGGERED"
    return (jsonify({"message":"Invalid Honey Token"}),404) if return_json else "INVALID"


@app.route("/honeytoken/<token_id>")
def trigger_honeytoken(token_id): return trigger_token(token_id, return_json=True)


@app.route("/api/dashboard-data")
@admin_required
def dashboard_data(): return jsonify(build_dashboard_payload())


@app.route("/api/block-ip", methods=["POST"])
@admin_required
def api_block_ip():
    ip=str((request.get_json(silent=True) or {}).get("ip_address","")).strip()
    if not ip: return jsonify({"success":False,"message":"IP address is required."}),400
    block_ip(ip, datetime.now().isoformat()); return jsonify({"success":True,"message":f"IP {ip} has been blocked.","ip_address":ip})


@app.route("/api/unblock-ip", methods=["POST"])
@admin_required
def api_unblock_ip():
    ip=str((request.get_json(silent=True) or {}).get("ip_address","")).strip()
    if not ip: return jsonify({"success":False,"message":"IP address is required."}),400
    unblock_ip(ip); return jsonify({"success":True,"message":f"IP {ip} has been unblocked.","ip_address":ip})


@app.route("/dashboard")
@admin_required
def dashboard():
    return render_template("dashboard.html", admin_username=session.get("admin_username", "admin"), server_ip=system_lan_ip())


@app.route("/health")
def health(): return jsonify({"status":"online","server_ip":system_lan_ip()})


if __name__ == "__main__":
    lan=system_lan_ip()
    print("\n=== Canary Token Security System ===")
    print("Local: http://127.0.0.1:5000")
    print(f"LAN:   http://{lan}:5000")
    print("Admin: /admin/login")
    print("User:  /user-dashboard")
    print("====================================\n")
    app.run(host="0.0.0.0", port=5000, debug=True)

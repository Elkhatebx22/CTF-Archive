"""
 Wizard King - internal magic desk backend.

This backend sits behind the Apache edge and keeps the desk state for tickets,
admin review, document previews, and owner verification.
"""

import datetime
import logging
import os
import re
import secrets
import subprocess
import threading
import time
from pathlib import Path
from urllib.parse import unquote

import pymysql
from flask import Flask, g, make_response, redirect, render_template, request, send_file, session, url_for
from gevent.pywsgi import WSGIServer
from werkzeug.serving import WSGIRequestHandler
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
app.secret_key = os.environ.get("CLOVER_SECRET_KEY", secrets.token_hex(32))

logging.basicConfig(level=logging.INFO, format="%(asctime)s app %(message)s")
logger = logging.getLogger("clover-app")

LOCK = threading.Lock()

ADMIN_USERNAME = os.environ.get("CLOVER_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("CLOVER_ADMIN_PASSWORD", "REDACTED")
BOT_TOKEN = "".join(os.environ.get("ASTA_TOKEN", "").split())
BOT_TOKEN_FILE = Path(os.environ.get("ASTA_TOKEN_FILE", "/secrets/bot_token"))

DB_HOST = os.getenv("DB_HOST", os.environ.get("CLOVER_DB_HOST", "db"))
DB_USER = os.getenv("DB_USER", os.environ.get("CLOVER_DB_USER", "clover"))
DB_PASSWORD = os.getenv("DB_PASSWORD", os.environ.get("CLOVER_DB_PASSWORD", "REDACTED"))
DB_NAME = os.getenv("DB_NAME", os.environ.get("CLOVER_DB_NAME", "clover"))
DB_PORT = os.getenv("DB_PORT", os.environ.get("CLOVER_DB_PORT", "3306"))
DB_WRITE_USER = os.getenv("DB_WRITE_USER", os.environ.get("CLOVER_DB_WRITE_USER", DB_USER))
DB_WRITE_PASSWORD = os.getenv("DB_WRITE_PASSWORD", os.environ.get("CLOVER_DB_WRITE_PASSWORD", DB_PASSWORD))

USERS = {
    "riley": {"password": "REDACTED", "role": "user"},
    ADMIN_USERNAME: {"password": ADMIN_PASSWORD, "role": "admin"},
}

SESSIONS = {}
if BOT_TOKEN:
    SESSIONS[BOT_TOKEN] = {"username": ADMIN_USERNAME, "role": "admin", "created": time.time()}

TICKETS = {}
_ticket_seq = {"next": 1}

MAX_TICKET_LENGTH = 4000
COOKIE_NAME = "clover_session"
ASSET_CACHE = Path(os.environ.get("CLOVER_ASSET_CACHE", "/app/cache/previews"))
ASSET_CACHE.mkdir(parents=True, exist_ok=True)
ASSET_CACHE_ROOT = ASSET_CACHE.resolve()
ALLOWED_UPLOAD_EXTENSIONS = {".txt", ".log", ".md", ".csv"}
ACCOUNT_PATTERN = r"^[a-zA-Z0-9\\ -]+$"
RESERVED_USERNAMES = {ADMIN_USERNAME.lower(), "owner"}

def _next_ticket_id():
    with LOCK:
        ticket_id = _ticket_seq["next"]
        _ticket_seq["next"] += 1
    return ticket_id


def _request_id():
    return request.headers.get("X-Request-ID", "-")


def current_session():
    token = request.cookies.get(COOKIE_NAME)
    if token and token in load_bot_tokens():
        with LOCK:
            SESSIONS[token] = {"username": ADMIN_USERNAME, "role": "admin", "created": time.time()}
    sess = SESSIONS.get(token)
    if sess:
        g.session_token = token
    return sess


def load_bot_tokens():
    tokens = set()
    if BOT_TOKEN:
        tokens.add(BOT_TOKEN)
    try:
        file_token = "".join(BOT_TOKEN_FILE.read_text().split())
    except OSError:
        file_token = ""
    if file_token:
        tokens.add(file_token)
    return tokens


def home_for_role(role):
    if role == "owner":
        return "/owner"
    if role == "admin":
        return "/admin"
    return "/tickets"


def issue_session(username, role):
    token = secrets.token_hex(32)
    with LOCK:
        SESSIONS[token] = {"username": username, "role": role, "created": time.time()}
    resp = make_response(redirect(home_for_role(role)))
    resp.set_cookie(COOKIE_NAME, token, httponly=True, samesite="Lax")
    return resp


def require_session():
    sess = current_session()
    if not sess:
        return None, redirect("/login")
    return sess, None


def require_admin():
    sess = current_session()
    if not sess:
        return None, redirect("/login")
    if sess["role"] not in ("admin", "owner"):
        return None, (render_template("403.html", username=sess["username"]), 403)
    return sess, None


def validate_account_input(username, password):
    if not re.match(ACCOUNT_PATTERN, username):
        raise Exception("Invalid username or password")

    if not re.match(ACCOUNT_PATTERN, password):
        raise Exception("Invalid username or password")


def validate_register_input(username, password):
    validate_account_input(username, password)
    if username.lower() in RESERVED_USERNAMES:
        raise Exception("Invalid username or password")


def safe_preview_path(preview_name):
    decoded = unquote(preview_name).replace("\\", "/")
    if not decoded or "\x00" in decoded:
        return None
    try:
        candidate = (ASSET_CACHE_ROOT / decoded).resolve()
        if not candidate.exists():
            return None
    except OSError:
        return None
    return candidate


@app.context_processor
def inject_layout_context():
    sess = current_session()
    username = sess["username"] if sess else None
    return {
        "current_user": username,
        "current_role": sess["role"] if sess else "anonymous",
    }


@app.template_filter("ts")
def format_timestamp(value):
    return datetime.datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")


@app.before_request
def log_request():
    sess = current_session()
    user = sess["username"] if sess else "anonymous"
    logger.info(
        "rid=%s method=%s path=%s user=%s",
        _request_id(),
        request.method,
        request.path,
        user,
    )


@app.after_request
def keep_session_cookie(resp):
    token = getattr(g, "session_token", None)
    if token and token in SESSIONS:
        resp.set_cookie(COOKIE_NAME, token, httponly=True, samesite="Lax")
    return resp


@app.route("/")
def index():
    sess = current_session()
    if sess:
        return redirect(home_for_role(sess["role"]))
    return redirect("/login")


@app.route("/register", methods=["GET"])
def register_form():
    return render_template("register.html", error=None)


@app.route("/register", methods=["POST"])
def register_submit():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    try:
        if not username or not password:
            raise Exception("Invalid username or password")
        validate_register_input(username, password)
        write_query(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, password),
        )
    except Exception:
        return render_template("register.html", error="Choose a new username and password."), 400
    return issue_session(username, "user")


@app.route("/login", methods=["GET"])
def login_form():
    sess = current_session()
    if sess:
        return redirect(home_for_role(sess["role"]))
    return render_template("login.html", error=None)


@app.route("/login", methods=["POST"])
def login_submit():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    try:
        validate_account_input(username, password)

        result = query(
            "SELECT username, role FROM users "
            "WHERE username = %s AND password = %s",
            (username, password),
        )

        if len(result) == 0:
            raise Exception("Invalid username or password")

    except Exception:
        logger.info(
            "rid=%s login failed for username=%s",
            _request_id(),
            username,
        )
        return render_template(
            "login.html",
            error="Invalid username or password."
        ), 401

    logger.info(
        "rid=%s login ok user=%s",
        _request_id(),
        username,
    )

    return issue_session(
        result[0]["username"],
        result[0].get("role", "user"),
    )


@app.route("/logout", methods=["POST"])
def logout():
    token = request.cookies.get(COOKIE_NAME)
    with LOCK:
        SESSIONS.pop(token, None)
    resp = make_response(redirect("/login"))
    resp.delete_cookie(COOKIE_NAME)
    return resp


@app.route("/tickets", methods=["GET"])
def list_tickets():
    sess, failure = require_session()
    if failure:
        return failure

    with LOCK:
        mine = list(TICKETS.values()) if sess["role"] in ("admin", "owner") else [
            t for t in TICKETS.values() if t["owner"] == sess["username"]
        ]
    mine.sort(key=lambda t: t["created"], reverse=True)
    return render_template("tickets.html", tickets=mine, username=sess["username"])


@app.route("/tickets/<int:ticket_id>", methods=["GET"])
def ticket_detail(ticket_id):
    sess, failure = require_session()
    if failure:
        return failure

    with LOCK:
        ticket = TICKETS.get(ticket_id)
        if ticket and sess["role"] in ("admin", "owner"):
            if ticket["status"] == "open":
                ticket["status"] = "reviewing"
                ticket["updated"] = time.time()
            elif ticket["status"] == "reviewing":
                ticket["status"] = "reviewed"
                ticket["updated"] = time.time()
        ticket_copy = dict(ticket) if ticket else None

    if not ticket_copy:
        return render_template("404.html", username=sess["username"]), 404

    if ticket_copy["owner"] != sess["username"] and sess["role"] not in ("admin", "owner"):
        return render_template("403.html", username=sess["username"]), 403

    return render_template("ticket_detail.html", ticket=ticket_copy, username=sess["username"])


@app.route("/create_ticket/new", methods=["POST"])
def create_ticket():
    sess, failure = require_session()
    if failure:
        return failure
    content = (request.form.get("ticket_content") or "").strip()[:MAX_TICKET_LENGTH]
    if not content:
        return render_template("tickets.html", tickets=[], username=sess["username"]), 400

    ticket_id = _next_ticket_id()
    now = time.time()
    with LOCK:
        TICKETS[ticket_id] = {
            "id": ticket_id,
            "owner": sess["username"],
            "content": content,
            "status": "open",
            "created": now,
            "updated": now,
        }

    logger.info("rid=%s ticket created id=%s owner=%s", _request_id(), ticket_id, sess["username"])
    return redirect(f"/tickets/{ticket_id}")


@app.route("/admin", methods=["GET"])
def admin_dashboard():
    sess, failure = require_admin()
    if failure:
        return failure

    with LOCK:
        all_tickets = sorted(TICKETS.values(), key=lambda t: t["created"], reverse=True)
    return render_template("admin.html", tickets=all_tickets, username=sess["username"])


@app.route("/admin/assets", methods=["GET"])
def admin_assets():
    sess, failure = require_admin()
    if failure:
        return failure
    files = sorted(p.name for p in ASSET_CACHE.iterdir() if p.is_file())
    return render_template("assets.html", files=files, username=sess["username"])


@app.route("/admin/assets", methods=["POST"])
def admin_assets_upload():
    sess, failure = require_admin()
    if failure:
        return failure
    upload = request.files.get("document")
    if not upload:
        return render_template("assets.html", files=[], error="Choose a document to upload.", username=sess["username"]), 400
    filename = secure_filename(upload.filename or "document.txt") or "document.txt"
    if Path(filename).suffix.lower() not in ALLOWED_UPLOAD_EXTENSIONS:
        files = sorted(p.name for p in ASSET_CACHE.iterdir() if p.is_file())
        return render_template("assets.html", files=files, error="Only txt, log, md, and csv previews are allowed.", username=sess["username"]), 400
    upload.save(ASSET_CACHE_ROOT / filename)
    return redirect(f"/admin/assets/preview/{filename}")


@app.route("/admin/assets/preview/<path:preview_name>", methods=["GET"])
def admin_assets_preview(preview_name):
    sess, failure = require_admin()
    if failure:
        return failure
    preview_path = safe_preview_path(preview_name)
    if not preview_path or not preview_path.is_file():
        return render_template("404.html", username=sess["username"]), 404
    return send_file(preview_path, mimetype="text/plain")


@app.route("/access", methods=["GET"])
def access_map():
    sess = current_session()
    return render_template(
        "access.html",
        username=sess["username"] if sess else None,
        role=sess["role"] if sess else "anonymous",
    )


def _run_mariadb(sql, db_user, db_password):
    data = []
    result = None
    try:
        result = subprocess.check_output(
            [
                "mariadb",
                "-h" + DB_HOST,
                "-u" + db_user,
                "-p" + db_password,
                "-e",
                sql,
                "--batch",
                "--ssl=0",
                DB_NAME,
            ]
        )
    except subprocess.CalledProcessError:
        raise Exception("Failed to execute query")

    result = result.decode("utf-8").splitlines()
    if len(result) == 0:
        return []

    columns = result[0].split("\t")

    for row in result[1:]:
        row = row.split("\t")
        if len(row) != len(columns):
            raise Exception("Invalid row")
        data.append({columns[i]: row[i] for i in range(len(columns))})

    return data


def _run_prepared(sql, params, db_user, db_password):
    try:
        with pymysql.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=db_user,
            password=db_password,
            database=DB_NAME,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                if cursor.description:
                    return list(cursor.fetchall())
            conn.commit()
            return []
    except pymysql.MySQLError:
        raise Exception("Failed to execute query")


def query(sql, params=None):
    if params is not None:
        return _run_prepared(sql, params, DB_USER, DB_PASSWORD)
    return _run_mariadb(sql, DB_USER, DB_PASSWORD)


def write_query(sql, params=None):
    if params is not None:
        return _run_prepared(sql, params, DB_WRITE_USER, DB_WRITE_PASSWORD)
    return _run_mariadb(sql, DB_WRITE_USER, DB_WRITE_PASSWORD)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    sess, failure = require_admin()
    if failure:
        return failure

    if request.method == "GET":
        return render_template("admin_login.html", error=None, username=sess["username"])
    elif request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]

            validate_account_input(username, password)

            result = query(f"SELECT username, role FROM users WHERE username = '{username}' AND password = '{password}'")
            if len(result) == 0:
                raise Exception("Invalid username or password")
            session["username"] = result[0]["username"]

            role = result[0].get("role", "owner")
            if session["username"] == "owner":
                role = "owner"
            elif role not in ("admin", "owner"):
                raise Exception("Invalid username or password")

            token = request.cookies.get(COOKIE_NAME)
            with LOCK:
                SESSIONS[token] = {"username": session["username"], "role": role, "created": time.time()}
            return redirect(url_for("index"))
        except Exception as exc:
            return render_template("admin_login.html", error="Invalid username or password.", username=sess["username"]), 401

    return render_template("admin_login.html", error="Invalid request method", username=sess["username"]), 405


@app.route("/owner", methods=["GET"])
def owner_panel():
    sess = current_session()
    if not sess or sess["role"] != "owner":
        return render_template("403.html", username=sess["username"] if sess else None), 403
    return render_template(
        "owner.html",
        username=sess["username"],
        fake_flag="REDACTED",
    )


@app.errorhandler(404)
def not_found(_err):
    return render_template("404.html", username=None), 404


@app.errorhandler(403)
def forbidden(_err):
    return render_template("403.html", username=None), 403


class KeepAliveRequestHandler(WSGIRequestHandler):
    protocol_version = "HTTP/1.1"


if __name__ == "__main__":
    WSGIServer(("0.0.0.0", 5000), app).serve_forever()

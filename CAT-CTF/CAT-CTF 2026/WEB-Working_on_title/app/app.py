import os
import re
from html import unescape

import requests
from flask import Flask, request, render_template

app = Flask(__name__)

REJECTED_CHARS = set("\"#(){}[]|\\:;,?/ \t\r\n")
EVENT_HANDLER_ASSIGNMENT = re.compile(r"\bon[a-z0-9_:-]+\s*=")
BOT_URL = os.environ.get("BOT_URL", "http://bot:9001/visit")
BOT_ALLOWED_PREFIX = os.environ.get("BOT_ALLOWED_PREFIX", "http")
BOT_REQUEST_TIMEOUT = float(os.environ.get("BOT_REQUEST_TIMEOUT", "30"))
CSP = "default-src 'self'; script-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'none'"


def normalize_input(value):
    normalized = value
    for _ in range(3):
        decoded = unescape(normalized)
        if decoded == normalized:
            break
        normalized = decoded
    return normalized.casefold()


def validate_input(user_input):
    normalized_input = normalize_input(user_input)
    rejected_char = next(
        (
            char
            for value in (user_input, normalized_input)
            for char in value
            if char in REJECTED_CHARS
        ),
        None,
    )
    if rejected_char:
        return f"Input rejected: Contains rejected character ({rejected_char})."

    if EVENT_HANDLER_ASSIGNMENT.search(normalized_input):
        return "Input rejected: Contains event handler assignment."

    return ""


@app.after_request
def add_csp(response):
    response.headers["Content-Security-Policy"] = CSP
    return response


@app.get("/")
def index():
    html = request.args.get("html", "")
    error = validate_input(html) if html else ""
    return render_template(
        "index.html",
        html=html,
        rendered_html="" if error else html,
        error=error,
        report_result="",
    )


@app.get("/report")
def report():
    url = request.args.get("url", "")
    report_result = ""
    error = ""

    if url:
        if not url.startswith(BOT_ALLOWED_PREFIX):
            error = f"Report rejected: URL must start with {BOT_ALLOWED_PREFIX}."
        else:
            try:
                response = requests.post(BOT_URL, data={"url": url}, timeout=BOT_REQUEST_TIMEOUT)
                report_result = response.text
            except requests.RequestException:
                error = "Report failed: bot is unavailable."

    return render_template(
        "index.html",
        html="",
        rendered_html="",
        error=error,
        report_result=report_result,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

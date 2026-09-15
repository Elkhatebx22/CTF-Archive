#!/usr/bin/env python3

import json
import os
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


PORT = int(os.environ.get("PORT", "3000"))
EDITORIAL_ACCESS_TOKEN_FILE = os.environ.get(
    "EDITORIAL_ACCESS_TOKEN_FILE", "/run/commonplace-access/token"
)
with open(EDITORIAL_ACCESS_TOKEN_FILE, encoding="ascii") as token_file:
    EDITORIAL_ACCESS_TOKEN = token_file.read().strip()
if re.fullmatch(r"[A-Za-z0-9_-]{32,128}", EDITORIAL_ACCESS_TOKEN) is None:
    raise RuntimeError("editorial access token must contain 32..128 safe characters")

MEMO_BODY = json.dumps(
    {
        "workspace": "Commonplace Editorial Operations",
        "url": "/operations/",
        "accessCode": EDITORIAL_ACCESS_TOKEN,
    },
    separators=(",", ":"),
)
COMPANION_ORIGIN = os.environ.get(
    "COMPANION_ORIGIN", "chrome-extension://dpmmgjgocnenankmgchlmkabpnbgpgmd"
)
CONNECTION_TTL_SECONDS = float(os.environ.get("CONNECTION_TTL_SECONDS", "300"))
DOCUMENT_PATTERN = re.compile(r"^[0-9a-f]{32}$")

connection_lock = threading.Lock()
connections = {}


def valid_web_origin(value):
    if not isinstance(value, str) or len(value) > 2048:
        return False
    try:
        parsed = urlparse(value)
        return bool(
            parsed.scheme in ("http", "https")
            and parsed.hostname
            and not parsed.username
            and not parsed.password
            and parsed.path in ("", "/")
            and not parsed.params
            and not parsed.query
            and not parsed.fragment
        )
    except ValueError:
        return False


def valid_document(value):
    return isinstance(value, str) and DOCUMENT_PATTERN.fullmatch(value) is not None


def connection_active(origin, document):
    now = time.monotonic()
    with connection_lock:
        expired = [key for key, deadline in connections.items() if deadline <= now]
        for key in expired:
            connections.pop(key, None)
        return bool(origin and valid_document(document) and connections.get((origin, document), 0) > now)


class Handler(BaseHTTPRequestHandler):
    server_version = "EditorialDesk/1.0"

    def log_message(self, format_string, *args):
        if self.path != "/health":
            print(f"[desk] {self.address_string()} {format_string % args}")

    def request_json(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 0 or size > 4096:
                return None
            return json.loads(self.rfile.read(size) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return None

    def parsed_request(self):
        return urlparse(self.path)

    def requested_document(self):
        values = parse_qs(self.parsed_request().query, keep_blank_values=True).get("document", [])
        if len(values) != 1 or not valid_document(values[0]):
            return None
        return values[0]

    def security_headers(self, resource_policy="same-origin"):
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
        )
        self.send_header("Cross-Origin-Resource-Policy", resource_policy)
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")

    def cors_headers(self, origin, methods, headers=None, private_network=False):
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", methods)
        if headers:
            self.send_header("Access-Control-Allow-Headers", headers)
        if private_network:
            self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Access-Control-Max-Age", "5")
        self.send_header("Vary", "Origin, Access-Control-Request-Private-Network")

    def send_json(self, status, value, cors_origin=None, resource_policy="same-origin"):
        payload = json.dumps(value, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.security_headers(resource_policy)
        if cors_origin:
            self.send_header("Access-Control-Allow-Origin", cors_origin)
            self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        parsed = self.parsed_request()
        origin = self.headers.get("Origin")
        private_network = (
            self.headers.get("Access-Control-Request-Private-Network", "").lower()
            == "true"
        )

        if parsed.path == "/api/connections" and not parsed.query and origin == COMPANION_ORIGIN:
            self.send_response(204)
            self.security_headers()
            self.cors_headers(origin, "POST", "Content-Type", private_network)
            self.end_headers()
            return

        document = self.requested_document()
        if parsed.path == "/api/memo" and connection_active(origin, document):
            self.send_response(204)
            self.security_headers("cross-origin")
            self.cors_headers(origin, "GET", private_network=private_network)
            self.end_headers()
            return

        self.send_json(403, {"error": "not authorized"})

    def do_GET(self):
        parsed = self.parsed_request()
        if parsed.path == "/health" and not parsed.query:
            self.send_json(200, {"status": "ready"})
            return

        if parsed.path == "/api/memo":
            origin = self.headers.get("Origin")
            document = self.requested_document()
            if not connection_active(origin, document):
                self.send_json(403, {"error": "not authorized"})
                return
            self.send_json(
                200,
                {"memo": MEMO_BODY},
                cors_origin=origin,
                resource_policy="cross-origin",
            )
            return

        self.send_json(404, {"error": "not found"})

    def do_POST(self):
        parsed = self.parsed_request()
        if parsed.path != "/api/connections" or parsed.query:
            self.send_json(404, {"error": "not found"})
            return

        if self.headers.get("Origin") != COMPANION_ORIGIN:
            self.send_json(403, {"error": "not authorized"})
            return

        data = self.request_json()
        origin = data.get("origin") if isinstance(data, dict) else None
        document = data.get("document") if isinstance(data, dict) else None
        if not valid_web_origin(origin) or not valid_document(document):
            self.send_json(400, {"error": "invalid connection"}, cors_origin=COMPANION_ORIGIN)
            return

        with connection_lock:
            connections[(origin, document)] = time.monotonic() + CONNECTION_TTL_SECONDS
        self.send_json(200, {"connected": True}, cors_origin=COMPANION_ORIGIN)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

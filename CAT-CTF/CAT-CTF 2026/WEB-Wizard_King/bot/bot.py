"""Wizard King admin reviewer bot."""

import logging
import os
import socket
import time
from pathlib import Path
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s bot %(message)s")
logger = logging.getLogger("asta")

EDGE_URL = os.environ.get("ASTA_URL", "http://web:8080")
BOT_TOKEN = "".join(os.environ["ASTA_TOKEN"].split())
BOT_TOKEN_FILE = Path(os.environ.get("ASTA_TOKEN_FILE", "/secrets/bot_token"))
REVIEW_INTERVAL_SECONDS = int(os.environ.get("ASTA_BOT_INTERVAL", "10"))


def current_bot_token() -> str:
    try:
        file_token = "".join(BOT_TOKEN_FILE.read_text().split())
    except OSError:
        file_token = ""
    return file_token or BOT_TOKEN


def visit_tickets() -> None:
    target = urlparse(EDGE_URL)
    host = target.hostname or "traefik"
    port = target.port or 8080
    token = current_bot_token()
    request = (
        "GET /tickets HTTP/1.1\r\n"
        f"Host: {target.netloc}\r\n"
        "User-Agent: AstaBot/1.0\r\n"
        f"Cookie: clover_session={token}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode()
    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            sock.sendall(request)
            sock.settimeout(5)
            sock.recv(4096)
        logger.info("visited /tickets through proxy")
    except OSError as exc:
        logger.info("could not reach tickets through proxy: %s", exc)


def main() -> None:
    logger.info("starting asta bot against %s", EDGE_URL)
    while True:
        visit_tickets()
        time.sleep(REVIEW_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()

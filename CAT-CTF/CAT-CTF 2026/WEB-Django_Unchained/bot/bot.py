import os
import time

import requests
from playwright.sync_api import sync_playwright


BOT_QUEUE_URL = os.environ.get("BOT_QUEUE_URL", "http://web:8000/bot/next/")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "local-bot-token")
LOGIN_URL = os.environ.get("LOGIN_URL", "http://app.cat26.local/login/")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "reviewer")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_PASSWORD_FILE = os.environ.get("ADMIN_PASSWORD_FILE", "/app/data/admin_password")


def admin_password():
    if ADMIN_PASSWORD:
        return ADMIN_PASSWORD
    try:
        with open(ADMIN_PASSWORD_FILE, "r", encoding="utf-8") as fp:
            return fp.read().strip()
    except OSError:
        return ""


def next_url():
    try:
        r = requests.get(BOT_QUEUE_URL, headers={"X-Bot-Token": BOT_TOKEN}, timeout=5)
        r.raise_for_status()
        return r.text.strip()
    except requests.RequestException as exc:
        print(f"queue error: {exc}", flush=True)
        return ""


def visit_url(browser, url):
    context = browser.new_context()
    page = context.new_page()
    try:
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=10000)
        password = admin_password()
        if not password:
            print("admin password not ready", flush=True)
            time.sleep(2)
            return
        page.fill("input[name=username]", ADMIN_USERNAME)
        page.fill("input[name=password]", password)
        page.click("button")
        page.goto(url, wait_until="domcontentloaded", timeout=10000)
        page.wait_for_timeout(2500)
        print(f"visited {url}", flush=True)
    finally:
        context.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--host-resolver-rules=MAP *.cat26.local nginx,MAP cat26.local nginx"],
        )

        while True:
            url = next_url()
            if not url:
                time.sleep(2)
                continue

            try:
                visit_url(browser, url)
            except Exception as exc:
                print(f"visit failed for {url}: {exc}", flush=True)


if __name__ == "__main__":
    main()

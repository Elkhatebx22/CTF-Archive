#!/usr/bin/env python3
import re
import sys
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = sys.argv[1] if len(sys.argv) > 1 else "https://quivera.b4nk4.tech/"
PROXIES = None
# PROXIES = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}


def solve():
    s = requests.Session()
    if PROXIES:
        s.proxies.update(PROXIES)
        s.verify = False

    resp = s.get(URL)

    flag = re.search(r"CTF\{[^\}]+\}", resp.text, re.IGNORECASE)
    if flag:
        print(flag.group(0))


if __name__ == "__main__":
    solve()

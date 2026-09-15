from flask import Flask, request, jsonify, session, render_template, redirect, url_for,abort
from parser import parse_cookie_header
import os
from requests import post
import secrets
from functools import wraps


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'lax'

users = {'admin':secrets.token_hex(32),}
print(users['admin'])
os.environ['admin_pass'] = users['admin']
sessions = {}
notes = {'admin':os.environ['flag'] if os.environ['flag'] else 'CATF{test}'}
cookies = ""

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def extract_cookies():
    global cookies
    cookies = parse_cookie_header(request.headers.get("Cookie")) if request.headers.get("Cookie") else None

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template("register.html", error="Missing fields")
        if username in users:
            return render_template("register.html", error="User exists")
        users[username] = password
        notes[username] = ""
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if users.get(username) == password:
            session['username'] = username
            if username == "admin":
                session['flag'] = os.environ.get('flag')
            return redirect(url_for('edit'))
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/notes', methods=['POST','GET'])
@auth_required
def notes_view():
    username = session['username']
    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            return "Content Can't be empty"
        notes[username] = content
        return notes[username]
    elif request.args.get("username"):
        return notes[request.args.get("username")] if notes[request.args.get("username")] else None
    return notes[username]

@app.route('/edit', methods=['GET'])
@auth_required
def edit():
    username = session['username']
    return render_template("edit.html", content=notes.get(username, ""))

@app.route("/log")
def log():
    data = request.args.get("data")
    try:
        with open("/tmp/logs.txt","b") as logfile:
            logfile.write(data)
        return jsonify({"logid":cookies.get("logid") if cookies else None, "Success":True})
        
    except:
        return jsonify({"logid":cookies.get("logid") if cookies else None, "Success":False})

@app.route("/auth/me")
@auth_required
def auth():
    return session['username']

@app.route("/bot")
def bot():
    username = session.get("username")
    if username:
        if "Visited successfully" in post("http://bot:3000/visit",json={'username':"admin",'password':users['admin'],'note':username}).text:
            return "Success"
        else:
            return "Fails"
    else:
        return "You're not logged in"
if __name__ == "__main__":
    app.run(port=5000,host="0.0.0.0")

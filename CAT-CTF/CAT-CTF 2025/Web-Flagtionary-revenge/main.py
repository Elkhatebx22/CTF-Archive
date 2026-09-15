from flask import Flask, request, jsonify, abort, render_template
from db import db

app = Flask(__name__)

database = db(black_list=['flag'])

setup_queries = [
    "INSERT INTO dict(word, meaning) VALUES('flag', 'CATF{lol_he_forgot_the_SQLi}')",
    "INSERT INTO dict(word, meaning) VALUES('TS', 'Type Script')",
    "INSERT INTO dict(word, meaning) VALUES('PW', 'Password')",
    "INSERT INTO dict(word, meaning) VALUES('JS', 'Java Script')",
]

database.setup(queries=setup_queries)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/api/search', methods=['POST'])
def search():
    word = request.get_json(force=False, silent=False)['word']
    if word is None:
        return jsonify({'error': 'Missing or invalid JSON'}), 400

    if "'" in word or len(word)!=2 :
        return abort(400)
    else:
        try:
            result =  database.query(f"SELECT meaning FROM dict WHERE word=?",word)
            return result if result else "None"
        except:
            return "Some security violation detected"
        
if __name__ == "__main__":
    app.run(port=9000,debug=True)

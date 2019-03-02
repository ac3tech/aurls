port = 5005
key_length = 5

import sqlite3
from colorama import init, Fore, Back, Style
init()
import os 
from flask import Flask, send_file, abort, redirect
app = Flask(__name__)
from gevent.pywsgi import WSGIServer
import random
import string

print(Style.BRIGHT+Fore.GREEN+"URLSIMP by Gradyn Wursten"+Style.RESET_ALL)
db = None
db_cursor = None
if not os.path.exists("links.db"):
    print("Database does not exist! Creating it..")
    db = sqlite3.connect('links.db')
    db_cursor = db.cursor()
    db_cursor.execute("CREATE TABLE links (key, value)")
else:
    db = sqlite3.connect('links.db')
    db_cursor = db.cursor()
print("Connected to database")

@app.route("/")
def root():
    return send_file('index.html')
@app.route("/SAVE/<path:value>")
def save(value):
    key = None
    t = (value,)
    if len(db_cursor.execute("SELECT * FROM links where value=?", t).fetchall()) == 0:
        loop = True
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=key_length))
        while loop:
            if not len(db_cursor.execute("SELECT * FROM links where key=?", t).fetchall()) == 0:
                key = ''.join(random.choices(string.ascii_letters + string.digits, k=key_length))
                loop = True
            else:
                loop = False
        db_cursor.execute(f"INSERT INTO links VALUES ('{key}',?)", t)
        db.commit()
    else: 
        key = db_cursor.execute("SELECT * FROM links where value=?", t).fetchone()[0]
    return(key)
@app.route("/<path:key>")
def load(key):
    t=(key,)
    if len(db_cursor.execute("SELECT * FROM links where key=?", t).fetchall()) == 0:
        abort(404)
    else:
        value = db_cursor.execute("SELECT * FROM links where key=?", t).fetchone()[1]
        if not value.startswith("http://") and not value.startswith("https://"):
            value = "http://" + value
        return redirect(value, code=302)

http_server = WSGIServer(('', port), app)
print(f"Running WSGI Server on port {port}")
http_server.serve_forever()

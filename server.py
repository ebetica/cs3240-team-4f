import sqlite3
import time
import os
import server_tools
import string
import random
from constants import *
from flask import Flask, request, g, send_from_directory, redirect, url_for
from werkzeug import utils

# Creats the application
app = Flask(__name__)

# The database location is stored here. If you move around files and
# don't change this, the server will break.
app.config.update(dict(
    DATABASE='database.db',
    DATABASE_SCHEMA='schema.sql',
    TESTING = False,
    DEBUG = True,
    USERS = {} # Stores list of logged in users and their timestamps
               # not sure if I'm putting this in the right place.
))

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource(app.config['DATABASE_SCHEMA']) as f:
            db.cursor().executescript(f.read())
        db.commit()


def query_db(query, args=(), one=False):
    """Returns a query to the database as a list"""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    get_db().commit()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/user_in_database', methods=['GET', 'POST'])
def user_in_database():
    """Tests if the user is in the database"""
    username = request.form['username']
    user = query_db("SELECT * FROM users WHERE username=?", [username], one=True )
    if user is not None:
        ret = TRUE
    else:
        ret = FALSE
    return ret

@app.route('/user_is_admin', methods=['GET', 'POST'])
def user_is_admin():
    """Tests if the user is in the database"""
    username = request.form['username']
    user_type = query_db("SELECT role FROM users WHERE username=?", [username], one=True )
    if user_type == 'user':
        ret = FALSE
    else:
        ret = TRUE
    return ret

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        username = request.form['username']
        userhash = request.form['hash']
        timestamp = request.form['timestamp']
        afile = request.files['file']
        listingFile = '.filelisting.onedir'

        if afile:  # and hash == serverHash: TODO
            filename = utils.secure_filename(afile.filename)
            descriptor = os.path.join(app.root_path, 'uploads', username)
            if not os.path.isdir(descriptor):
                os.mkdir(descriptor, 0700)
            descriptor1 = os.path.join(descriptor, listingFile)
            with open(descriptor1, 'a') as listFile:
                listFile.write(filename + ' ' + timestamp)
            descriptor2 = os.path.join(descriptor, filename)
            afile.save(descriptor2)
            return redirect(url_for('uploaded_file',
                                        filename=filename))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    username = request.form['username']
    userhash = request.form['hash']
    #if hash == serverHash: TODO
    descriptor = os.path.join(app.root_path, 'uploads', username)
    return send_from_directory(descriptor, filename)

@app.route('/sync')
def client_sync():
    username = request.form['username']
    userhash = request.form['hash']
    listingFile = '.filelisting.onedir'
    #if hash == serverHash: TODO
    descriptor = os.path.join(app.root_path, 'uploads', username)
    return send_from_directory(descriptor, listingFile)


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    user = query_db("SELECT * FROM users WHERE username=?", [username], one=True )
    if user is None: return FALSE
    if user[1] == server_tools.password_hash(request.form['password']):
        letters = string.ascii_letters+string.digits
        h = "".join([random.choice(letters) for k in range(20)])
        app.config['USERS'][user[0]] = [time.time(), h]
        if app.config["DEBUG"]: print app.config
        return h
    else:
        return FALSE


@app.route('/register', methods=['POST'])
def register():
    username= request.form['username']
    password= server_tools.password_hash(request.form['password'])
    email = request.form['email']
    user=request.form['user_type']
    query_db("INSERT INTO users VALUES (?,?,?,?)",[username,password,email,user],one=True)
    # Code for registering a user.
    # Read from form sent in via post, hash the password
    # and make entry to database.
    return TRUE

@app.route('/getVals',methods=['GET'])
def getVals():
    item=request.form['item']
    Vals=query_db("SELECT * FROM ?",[item], one=True)
    return Vals

@app.route('/post', methods=['POST'])
def post():
    file = request.form['file']
    query_db("")

@app.route('/password_reset', methods=['POST'])
def password_reset():
    username = request.form['username']
    query_db("UPDATE users SET password = 'password' WHERE username = (?)",[username],one=True)

@app.route('/password_change', methods=['POST'])
def password_change():
    username = request.form['username']
    user = query_db("SELECT * FROM users WHERE username=?", [username], one=True )
    if user[1] == server_tools.password_hash(request.form['oldpass']):
        password = server_tools.password_hash(request.form['newpass'])
        query_db("UPDATE users SET password = (?) WHERE username = (?)", [password, username], one=True)
        return TRUE
    else: return FALSE

@app.route('/remove_user', methods=['POST'])
def remove_user():
    username = request.form['username']
    query_db("DELETE FROM users WHERE username = (?)", [username],one=True)

if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"])

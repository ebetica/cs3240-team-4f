import sqlite3
import time
import os
import hashlib
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

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        afile = request.files['file']
        if afile:
            filename = utils.secure_filename(afile.filename)
            descriptor = os.path.join(app.root_path, 'uploads/', filename)
            afile.save(descriptor)
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    descriptor = os.path.join(app.root_path, 'uploads/')
    return send_from_directory(descriptor, filename)


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    user = query_db("SELECT * FROM users WHERE username=?", [username], one=True )
    if user is None: return FALSE
    if user[1] == _password_hash(request.form['password']):
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
    password= _password_hash(request.form['password'])
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
@app.route('/remove_user', methods=['POST'])
def remove_user():
    username = request.form['username']
    query_db("DELETE FROM users WHERE username = (?)", [username],one=True)

def _password_hash(password):
    # Make this return the proper hashed version later
    # Probably use SHA1 with salt
    return hashlib.sha1(password).hexdigest()


if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"])

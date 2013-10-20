import sqlite3
import time

from flask import Flask, request, g


# Creats the application
app = Flask(__name__)

app.config.update(dict(
    DATABASE='data/database.db',
    DATABASE_SCHEMA='data/schema.sql',
    TESTING = False,
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
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/user_in_database', methods=['GET', 'POST'])
def user_in_database():
    username = request.form['username']
    user = query_db("SELECT * FROM users WHERE username=?", [username], one=True )
    ret = True if user != None else False
    return ret


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    user = query_db("SELECT * FROM users WHERE username=?", [username], one=True )
    if user[1] == _password_hash(request.form['password']):
        app.config['USERS'][user[0]] = time.time()
        print app.config
        return True
    else:
        return False


@app.route('/register', methods=['POST'])
def register():
    username= request.form['username']
    password= _password_hash(request.form['password'])
    email = request.form['email']
    query_db("INSERT INTO user VALUES (?,?,?)",[username,password,email],one=True)
    # Code for registering a user.
    # Read from form sent in via post, hash the password
    # and make entry to database.
    return True


def _password_hash(password):
    # Make this return the proper hashed version later
    # Probably use SHA1 with salt
    return password


if __name__ == '__main__':
    app.run()

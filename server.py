import sqlite3, time, os, string, random, uuid
import server_tools
from constants import *
from flask import Flask, request, g, send_from_directory, render_template, redirect, url_for
from flask.ext.autoindex import AutoIndex

# Creats the application
app = Flask(__name__)
index = AutoIndex(app, add_url_rules=True)

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

@app.route('/index')
def web_home_page():
    return render_template('index.html')

@app.route('/web_login', methods=['POST'])
def web_login_page():
    hold = server_tools.login(request.form['username'], request.form['password'])
    if not hold:
        return FALSE
    else:
        user = hold[0]
        h = hold[1]
        if user[0] in app.config['USERS']:
            app.config['USERS'][user[0]].append({'time': time.time(), 'auth': h})
        else:
            app.config['USERS'][user[0]] = [{'time': time.time(), 'auth': h}]
        if app.config["DEBUG"]: print app.config
        if server_tools.user_is_admin(request.form['username']):
            return redirect(url_for('browse_all_uploads'), code=307)
        else:
            return redirect(url_for('browse_user_uploads', username=request.form['username'], auth=h), code=307)


@app.route('/uploads/<username>_<auth>', methods=['GET', 'POST'])
def browse_user_uploads(username, auth):
    if  auth in [i['auth'] for i in app.config['USERS'][username]]:
        return index.render_autoindex(os.path.join('uploads', username), browse_root=app.config.root_path)
    else:
        return FALSE

@app.route('/uploads/', methods=['GET', 'POST'])
def browse_all_uploads():
    if server_tools.user_is_admin(request.form['username']):

        return index.render_autoindex('uploads', browse_root=app.config.root_path)

@app.route('/user_in_database', methods=['GET', 'POST'])
def user_in_database():
    """Tests if the user is in the database"""
    username = request.form['username']
    val = server_tools.user_in_database(username)
    if val:
        ret = TRUE
    else:
        ret = FALSE
    return ret

@app.route('/user_is_admin', methods=['GET', 'POST'])
def user_is_admin():
    """Tests if the user is in the database"""
    username = request.form['username']
    val = server_tools.user_is_admin(username)
    if not val:
        ret = FALSE
    else:
        ret = TRUE
    return ret


@app.route('/listing')
def listing():
    if not securify(request):
        return FALSE
    username = request.form['username']
    listingFile = username + '.filelisting'
    listing_path = os.path.join(app.root_path, 'uploads', listingFile)
    try:
        return open(listing_path, 'r').read()
    except:
        return FALSE


@app.route('/upload', methods=['POST'])
def upload_file():
    # Uploads the file to the user's upload directory
    # Updates the listing file with the new upload!
    if not securify(request):
        return FALSE
    username = request.form['username']
    timestamp = request.form['timestamp']
    path = request.form['path']
    afile = request.files['file']

    if afile:
        descriptor = os.path.join(app.root_path, 'uploads', username)
        if not os.path.isdir(descriptor):
            os.mkdir(descriptor, 0700)
        server_tools.update_listings(username, path, timestamp)
        path = os.path.join(descriptor, path)
        server_tools.r_mkdir( os.path.dirname(path) )
        afile.save(path)
        print("Saved file to %s"%path)
        update_history(username, path, timestamp, "modify")
        return TRUE
    return FALSE

@app.route('/share')
def share_file(filename):
    username = request.form['username']
    path = request.form['PathName']
    userShared = request.form['SharedWith']
    sharedPath = os.path.join(app.root_path, 'uploads', userShared, 'Share', username)
    server_tools.r_mkdir(os.path.dirname(sharedPath))
    filePath = os.path.join(app.root_path, 'uploads', username, path)
    os.symlink(filePath, sharedPath)
    server_tools.update_listings(userShared, path, os.path.getmtime(sharedPath))
    return TRUE

@app.route('/delete')
def delete_file():
    if not securify(request):
        return FALSE
    username = request.form['username']
    rel_path = request.form['rel_path']
    descriptor = os.path.join(app.root_path, 'uploads', username, rel_path)

    server_tools.update_listings(username, rel_path, 0, True)

    if os.path.isfile(descriptor):
        os.remove(descriptor)
    if os.path.isdir(descriptor):
        os.rmdir(descriptor)
    update_history(username, rel_path, timestamp, "delete")
    return TRUE

@app.route('/mkdir', methods=['POST'])
def mkdir():
    if not securify(request):
        return FALSE
    username = request.form['username']
    descriptor = os.path.join(app.root_path, 'uploads', username, request.form['path'])
    server_tools.r_mkdir(descriptor)
    update_history(username, descriptor, timestamp, "mkdir")
    return TRUE


def update_history(user, path, timestamp, op):
    hist_file = os.path.join("uploads", user + '.history')
    with open(hist_file, 'a') as hist:
        hist.write("%s %s %s\n"%(timestamp, path, op))
        # Write the timestamp to the last updated field in the sql

@app.route('/download/<filename>')
def uploaded_file(filename):
    if not securify(request):
        return FALSE
    username = request.form['username']
    descriptor = os.path.join(app.root_path, 'uploads', username)
    return send_from_directory(descriptor, filename)

@app.route('/sync')
def client_sync():
    if not securify(request):
        return FALSE
    username = request.form['username']
    listingFile = '.filelisting.onedir'
    descriptor = os.path.join(app.root_path, 'uploads', username)
    return send_from_directory(descriptor, listingFile)


def securify(request):
    username = request.form['username']
    auth = request.form['auth']
    return auth in [i['auth'] for i in app.config['USERS'][username]]


@app.route('/login', methods=['GET','POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    hold = server_tools.login(username, password)
    if not hold:
        return FALSE
    else:
        user = hold[0]
        h = hold[1]
        if user[0] in app.config['USERS']:
            app.config['USERS'][user[0]].append({'time': time.time(), 'auth': h})
        else:
            app.config['USERS'][user[0]] = [{'time': time.time(), 'auth': h}]
        if app.config["DEBUG"]: print app.config
        return h

@app.route('/logout', methods=['POST'])
def logout():
    user = request.form['username']
    auth = request.form['auth']
    if user not in app.config['USERS']: return FALSE
    for i in app.config['USERS'][user]:
        if i['auth'] == auth:
            app.config['USERS'][user].remove(i)
            break
    return TRUE


@app.route('/register', methods=['POST'])
def register():
    username= request.form['username']
    salt = uuid.uuid1().hex
    password= server_tools.password_hash(request.form['password']+salt)
    email = request.form['email']
    user = request.form['user_type']
    query_db("INSERT INTO users VALUES (?,?,?,?,?)",[username,password,salt,email,user],one=True)
    # Code for registering a user.
    # Read from form sent in via post, hash the password
    # and make entry to database.
    return TRUE

@app.route('/getVals',methods=['GET'])
def getVals():
    value = request.form['value']
    table = request.form['table']
    query = "SELECT * FROM " + table
    vals = query_db( query, [], one=False)
    if value == 'username':
        return '\n'.join( val[0] for val in vals)
    else:
        return '\n'.join( val for val in vals)

@app.route('/password_reset', methods=['POST'])
def password_reset():
    username = request.form['username']
    query_db("UPDATE users SET password = 'password' WHERE username = (?)",[username],one=True)

@app.route('/password_change', methods=['POST'])
def password_change():
    username = request.form['username']
    user = query_db("SELECT * FROM users WHERE username=?", [username], one=True )
    if user[1] == server_tools.password_hash(request.form['oldpass']+user[2]):
        password = server_tools.password_hash(request.form['newpass'])
        query_db("UPDATE users SET password = (?) WHERE username = (?)", [password, username], one=True)
        return TRUE
    else: return FALSE

@app.route('/remove_user', methods=['POST'])
def remove_user():
    username = request.form['username']
    query_db("DELETE FROM users WHERE username = (?)", [username],one=True)

@app.route('/view_user_files', methods = ['GET'])
def view_user_files():
    username = request.form['username']
    path = os.path.join(app.root_path, 'uploads', username)
    return server_tools.view_files(path)

@app.route('/view_all_files', methods=['GET'])
def view_all_files():
    path = os.path.join(app.root_path,'uploads')
    return server_tools.view_files(path)

if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"])

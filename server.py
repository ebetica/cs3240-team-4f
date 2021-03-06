from constants import *
import server_tools

from flask import Flask, request, g, send_file, render_template, redirect, url_for
import os
import sqlite3
import time
import uuid

# Creates the application
app = Flask(__name__)

# The database location is stored here. If you move around files and
# don't change this, the server will break.
app.config.update(dict(
    DATABASE='database.db',
    DATABASE_SCHEMA='schema.sql',
    TESTING=False,
    DEBUG=True,
    USERS={}  # Stores list of logged in users and their timestamps
              # not sure if I'm putting this in the right place.
))

# Server-side database methods
##########


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        if error:
            print("There was an error closing the database")


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

# Web interface methods
##########
@app.errorhandler(400)
def bad_request(error):
    return '''<html lang="en"> <a href="/"> You are not logged in </a> </html>'''


@app.route('/browse/', methods=['GET', 'POST'])
def uploads(path=None):
    hold = server_tools.login(request.form['username'], request.form['password'])
    if not hold:
        return FALSE
    else:
        user = hold[0][0]
        h = hold[1]
        if user[0] in app.config['USERS']:
            app.config['USERS'][user].append({'time': time.time(), 'auth': h})
        else:
            app.config['USERS'][user] = [{'time': time.time(), 'auth': h}]
        directories = {}
        files = {}
        if server_tools.user_is_admin(request.form['username']):
            descriptor = os.path.join(app.root_path, 'uploads')
            for stuff in os.listdir(descriptor):
                if os.path.isdir(os.path.join(descriptor, stuff)):
                    directories[stuff] = stuff
                else:
                    files[stuff] = '/webdownload/' + stuff
        else:
            descriptor = os.path.join(app.root_path, 'uploads', user)
            for stuff in os.listdir(descriptor):
                if os.path.isdir(os.path.join(descriptor, stuff)):
                    directories[stuff] = user + '_' + stuff
                else:
                    if not stuff.startswith('.'): files[stuff] = '/webdownload/' + user + '_' + '_' + stuff
        path = os.path.relpath(descriptor, os.path.join(app.root_path, 'uploads'))
        return render_template('browse.html', directories=directories, files=files, path=path, user=user, auth=h)


@app.route('/browse/<path>', methods=['GET', 'POST'])
def browse_directories(path, aFile=None):
    auth = request.form['auth']
    user = request.form['username']
    authorized = str(path).split('_')[0] == user
    admin = server_tools.user_is_admin(user)
    if securify(request) and (authorized or admin):
        path = str(path).replace('_', '/')
        descriptor = os.path.join(app.root_path, 'uploads', path)
        directories = {}
        files = {}
        path = os.path.relpath(descriptor, os.path.join(app.root_path, 'uploads'))
        for stuff in os.listdir(descriptor):
                if os.path.isdir(os.path.join(descriptor, stuff)):
                    directories[stuff] = str(path).replace('/', '_') + '_' + stuff
                else:
                    if not stuff.startswith('.'): files[stuff] = '/webdownload/' + str(path).replace('/', '_') + '_' + stuff
        return render_template('browse.html', directories=directories, files=files, path=path, user=user, auth=auth)
    else:
        return '''<html lang="en"> <a href="/index"> You are not logged in </a> </html>'''

@app.route('/webdownload/<path>', methods=['GET', 'POST'])
def web_downloads(path, aFile=None):
    auth = request.form['auth']
    user = request.form['username']
    authorized = str(path).split('_')[0] == user
    admin = server_tools.user_is_admin(user)
    if securify(request) and (authorized or admin):
        path = str(path).replace('_', '/')
        descriptor = os.path.join(app.root_path, 'uploads', path)
        return send_file(descriptor)
    else:
        return '''<html lang="en"> <a href="/index"> You are not logged in </a> </html>'''

@app.route('/uploads/', methods=['GET', 'POST'])
def browse_all_uploads():
    """Allows admin users to browse the directory with all stored files through a web-browser"""
    if server_tools.user_is_admin(request.form['username']):
        return TRUE  # index.render_autoindex('uploads', browse_root=app.config.root_path)
    else:
        return "Perhaps you don't have privileges for that"

@app.route('/')
@app.route('/index')
def web_home_page():
    """Returns page where users can log into the application"""
    return render_template('index.html')  # index.html exists in the templates directory. Flask knows this.


@app.route('/web_login', methods=['POST'])
def web_login_page():
    """Parses form input to log the user in from the homepage and redirects to proper directory display"""
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
        if app.config["DEBUG"]:
            print app.config
        if server_tools.user_is_admin(request.form['username']):
            return redirect(url_for('browse_all_uploads'), code=307)
        else:
            return redirect(url_for('browse_user_uploads', username=request.form['username'], path='.', auth=h), code=307)


@app.route('/delete')
def delete_file():
    """Deletes the file specified in the request from the server"""
    if not securify(request):
        return FALSE
    username = request.form['username']
    rel_path = request.form['rel_path']
    timestamp = request.form['timestamp']
    descriptor = os.path.join(app.root_path, 'uploads', username, rel_path)

    server_tools.update_listings(username, rel_path, timestamp, True)

    if os.path.isfile(descriptor):
        os.remove(descriptor)
    if os.path.isdir(descriptor):
        os.rmdir(descriptor)
    timestamp = request.form['timestamp']
    server_tools.update_history(username, descriptor, timestamp, "delete")
    return TRUE


@app.route('/getVals', methods=['GET'])
def getVals():
    """Used to return attributes specified in request from the table"""
    if securify(request) and server_tools.user_is_admin(request.form['username']):
        value = request.form['value']
        table = server_tools.scrub_sqlite_input(request.form['table'])
        query = "SELECT * FROM " + table
        vals = query_db(query, [], one=False)
        if value == 'username':
            return '\n'.join(val[0] for val in vals)
        else:
            return '\n'.join(val for val in vals)
    else:
        return "You need to be an admin for this feature"


@app.route('/listing')
def listing():
    """Returns a listing of the user's files that are saved to the OneDir server"""
    if not securify(request):
        return FALSE
    username = request.form['username']
    listingFile = username + '.filelisting'
    listing_path = os.path.join(app.root_path, 'uploads', listingFile)
    if os.path.isfile(listing_path):
        return open(listing_path, 'r').read()
    else:
        f = open(listing_path, 'w')
        f.close()
        return ""


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs a user in to the OneDir service running on the server"""
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
        return h


@app.route('/logout', methods=['POST'])
def logout():
    """Logs a user out from the OneDir service running on the server"""
    user = request.form['username']
    auth = request.form['auth']
    if user not in app.config['USERS']:
        return FALSE
    for i in app.config['USERS'][user]:
        if i['auth'] == auth:
            app.config['USERS'][user].remove(i)
            server_tools.update_log(user, 'Logout')
            break
    return TRUE


@app.route('/mkdir', methods=['POST'])
def mkdir():
    """Creates a sub-directory in the user's server-side OneDir directory"""
    if not securify(request):
        return FALSE
    username = request.form['username']
    descriptor = os.path.join(app.root_path, 'uploads', username, request.form['path'])
    server_tools.r_mkdir(descriptor)
    server_tools.update_listings(username, request.form['path'], request.form['timestamp'])
    server_tools.update_history(username, descriptor, request.form['timestamp'], "mkdir")
    return TRUE


@app.route('/password_change', methods=['POST'])
def password_change():
    """Allows a user to change their own password"""
    if securify(request):
        username = request.form['username']
        user = query_db("SELECT * FROM users WHERE username=?", [username], one=True)
        if user[1] == server_tools.password_hash(request.form['oldpass'] + user[2]):
            password = server_tools.password_hash(request.form['newpass'] + user[2])
            query_db("UPDATE users SET password = (?) WHERE username = (?)", [password, username], one=True)
            return TRUE
        else:
            return FALSE


@app.route('/password_reset', methods=['POST'])
def password_reset():
    """Resets the user's password for the OneDir service"""
    username = request.form['username']
    if securify(request) and server_tools.user_is_admin(username):
        resetMe = request.form['resetMe']
        user = query_db("SELECT * FROM users WHERE username=?", [resetMe], one=True)
        password = server_tools.password_hash('password' + user[2])
        query_db("UPDATE users SET password = (?) WHERE username = (?)", [password, resetMe], one=True)
        return TRUE
    else:
        return FALSE


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    salt = uuid.uuid1().hex
    password = server_tools.password_hash(request.form['password']+salt)
    email = request.form['email']
    user = request.form['user_type']
    if not server_tools.user_in_database(username):
        query_db("INSERT INTO users VALUES (?,?,?,?,?)", [username, password, salt, email, user], one=True)
        try:
            os.mkdir(os.path.join(app.config, 'uploads', username))
            listingfile = username + '.filelisting'
            open(os.path.join(app.config, 'uploads', listingfile), 'w').close()
            return TRUE
        except IOError:
            return FALSE


@app.route('/remove_user', methods=['POST'])
def remove_user():
    """Removes a user from the OneDir service. Does not delete their files"""
    if securify(request) and server_tools.user_is_admin(request.form['username']):
        deleteMe = request.form['deleteMe']
        query_db("DELETE FROM users WHERE username = (?)", [deleteMe], one=True)
        return TRUE
    return "You need to be an admin user to use this feature"


def securify(request):
    username = request.form['username']
    auth = request.form['auth']
    if username not in app.config['USERS']: return False
    return auth in [i['auth'] for i in app.config['USERS'][username]]


@app.route('/share')
def share_file():
    """Shares the file from one user (username) with another (sharedUser)"""
    if not securify(request):
        return FALSE
    username = request.form['username']
    path = request.form['PathName']
    userShared = request.form['SharedWith']
    sharedPath = os.path.join(app.root_path, 'uploads', userShared, 'Share', username, path)
    server_tools.r_mkdir(os.path.dirname(sharedPath))
    filePath = os.path.join(app.root_path, 'uploads', username, path)
    os.symlink(filePath, sharedPath)
    server_tools.update_listings(userShared, path, os.path.getmtime(sharedPath))
    return TRUE


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
        server_tools.r_mkdir(os.path.dirname(path))
        afile.save(path)
        print("Saved file to %s" % path)
        server_tools.update_history(username, path, timestamp, "modify")
        return TRUE
    return FALSE


@app.route('/download', methods=['GET', 'POST'])
def download_file():
    """Returns the requested file from the user's server-side OneDir directory"""
    if not securify(request):
        return FALSE
    username = request.form['username']
    filename = request.form['filename']
    if '..' in filename or filename.startswith('/'):
        return FALSE
    descriptor = os.path.join(app.root_path, 'uploads', username, filename)
    print("Sending %s..." % descriptor)
    if os.path.isdir(descriptor): return TRUE 
    else: return send_file(descriptor)


@app.route('/user_is_admin', methods=['GET', 'POST'])
def user_is_admin():
    """Tests if the user is an admin user"""
    username = request.form['username']
    val = server_tools.user_is_admin(username)
    if not val:
        return FALSE
    else:
        return TRUE


@app.route('/user_in_database', methods=['GET', 'POST'])
def user_in_database():
    """Tests if the user is in the database"""
    username = request.form['username']
    val = server_tools.user_in_database(username)
    if not val:
        return FALSE
    else:
        return TRUE


@app.route('/view_user_files', methods=['GET'])
def view_user_files():
    """Returns a listing that contains the number and size of all files stored by a user"""
    if securify(request) and server_tools.user_is_admin(request.form['username']):
        viewUser = request.form['viewUser']
        path = os.path.join(app.root_path, 'uploads', viewUser)
        return server_tools.view_files(path)
    else:
        return "You need to be an admin for this feature"


@app.route('/view_all_files', methods=['GET'])
def view_all_files():
    """Returns a listing that contains the number and size of all files stored by the service"""
    if securify(request) and server_tools.user_is_admin(request.form['username']):
        path = os.path.join(app.root_path, 'uploads')
        return server_tools.view_files(path)
    else:
        return "You need to be an admin for this feature"


@app.route('/delete_user_files', methods=['POST'])
def delete_user_files():
    if securify(request) and server_tools.user_is_admin(request.form['username']):
        path = os.path.join(app.root_path, 'uploads', request.form['deleteMyFiles'])
        server_tools.delete_user_files(path, request.form['filename'])
    else:
        return "You need to be an admin for this feature"


@app.route('/get_admin_log', methods=['POST'])
def get_admin_log():
    if securify(request) and server_tools.user_is_admin(request.form['username']):
        path = os.path.join(app.root_path, 'uploads', '.admin.log')
        return send_file(path)
    else:
        return "You need to be an admin for this feature"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4414, debug=app.config["DEBUG"])

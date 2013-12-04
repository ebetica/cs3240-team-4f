# The non-interactive parts of the client
from constants import *
import daemon
import pynotify_update
import os
import requests
import shutil
import string
from threading import Timer
import time

DEBUG = False

# Server request related function
########

def file_listing():
    """Returns a listing of the files stored on the server in the user's directory"""
    url = SERVER_ADDRESS
    url += 'listing'
    payload = add_auth({})
    r = requests.get(url, data=payload)
    if r.content == FALSE:
        print("You are not logged in! Shutting down OneDir...")
        quit_session()
    return r.content


def get_user_list():
    """Returns the list of users registered on the OneDir server"""
    payload = {'value': 'username', 'table': 'users'}
    payload = add_auth(payload)
    r = requests.get(SERVER_ADDRESS+'getVals', data=payload)
    return r.content


def get_admin_log():
    """Returns the log of user activity on the OneDir server"""
    payload = add_auth({})
    r = requests.post(SERVER_ADDRESS+'get_admin_log', data=payload)
    filename = os.path.join(read_config_file(session()["username"]), 'OneDir.log')
    if r.content == FALSE:
    # Something went wrong with sending the file, mostly likely improper file path.
        return
    else:
        r_mkdir(os.path.dirname(filename))
        if os.path.isdir(filename):
            # BUG... I don't know why this happens
            return
        with open(filename, 'wb') as code:
            code.write(r.content)


def is_admin():
    """Returns if a user is an admin or not"""
    payload = add_auth({})
    r = requests.get(SERVER_ADDRESS + 'user_is_admin', data=payload)
    return r.content == TRUE


def login_user(username, password):
    """Logs a user in to the OneDir server"""
    payload = {'username': username, 'password': password}
    r = requests.post(SERVER_ADDRESS + 'login', data=payload)
    return r.content


def password_change(oldpass, newpass):
    """Change password from oldpass to newpass for input user"""
    payload = {'oldpass': oldpass, 'newpass': newpass}
    payload = add_auth(payload)
    r = requests.post(SERVER_ADDRESS + 'password_change', data=payload)
    return r.content == TRUE


def password_reset(resetMe):
    """Reset password for input user"""
    payload = {'resetMe': resetMe}
    payload = add_auth(payload)
    r = requests.post(SERVER_ADDRESS + 'password_reset', data=payload)
    return r.content == TRUE


def register_user(username, password, email=None, _type='user'):
    """Registers the user specified by username in the database"""
    if not user_in_database(username):
        if email is None:
            email = ''
        if sanity_check_username(username):
            payload = {'username': username, 'password': password, 'email': email, 'user_type': _type}
            r = requests.post(SERVER_ADDRESS + 'register', data=payload)
            return r.status_code
        else:
            pass
            #toss error or re-enter.


def remove_user(deleteMe):
    """Remove users from the OneDir service"""
    payload = {'deleteMe': deleteMe}
    payload = add_auth(payload)
    r = requests.post(SERVER_ADDRESS + 'remove_user', data=payload)
    return r.content == TRUE


def share_file(user, pathName):
    """Shares the file located at pathname from the current user to the input user"""
    url = SERVER_ADDRESS + 'share'
    payload = add_auth({'SharedWith': user, 'PathName': pathName})
    r = requests.post(url, data=payload)
    return r.status_code


def upload_file(filename, timestamp):
    """Uploads the file specified by filename and its timestamp to the server"""
    url = SERVER_ADDRESS
    sess = session()
    ONEDIR_DIRECTORY = read_config_file(sess['username'])
    rel_path = os.path.relpath(filename, ONEDIR_DIRECTORY)
    payload = add_auth({'timestamp': timestamp, 'path': rel_path})
    files = {}
    if os.path.isdir(filename):
        url += 'mkdir'
    else:
        url += 'upload'
        if not os.path.exists(filename):
            print("File disappeared before I could upload it!")
            return
        files = {'file': open(filename, 'rb')}
    r = requests.post(url, files=files, data=payload)
    update_listings(sess['username'], rel_path, timestamp)
    if r.content == FALSE:
        print("You are not logged in! Shutting down OneDir...")
        quit_session()
    return r.status_code


def delete_file(filename):
    """Deletes specified file from the server, if this file has been deleted from the user's OneDir directory"""
    url = SERVER_ADDRESS
    url += 'delete'
    sess = session()
    onedir_directory = read_config_file(sess['username'])
    rel_path = os.path.relpath(filename, onedir_directory)
    timestamp = time.time()
    payload = add_auth({'timestamp': timestamp, 'rel_path': rel_path})

    r = requests.get(url, data=payload)
    update_listings(sess['username'], rel_path, timestamp)
    if r.content == FALSE:
        print("You are not logged in! Shutting down OneDir...")
        quit_session()
    return r.status_code


def delete_user_files(user, filename):
    url = SERVER_ADDRESS
    url += 'delete_user_files'
    payload = add_auth({'deleteMyFiles': user, 'filename': filename})
    r = requests.post(url, data=payload)
    return r.status_code


def download_file(filename):
    """ Downloads file specified by filename from the OneDir server
        The argument is a relative path to the filename"""
    if filename == "":
        return
    url = SERVER_ADDRESS
    url += 'download'
    payload = add_auth({'filename': filename})
    r = requests.get(url, data=payload)
    if r.content == FALSE:
        print("You are not logged in! Shutting down OneDir...")
        quit_session()
        return
    update_listings(session()['username'], filename, time.time())
    filename = os.path.join(read_config_file(session()["username"]), filename)
    if r.content == TRUE:
        r_mkdir(filename)
    elif r.content == FALSE:
    # Something went wrong with sending the file, mostly likely improper file path.
        return
    else:
        r_mkdir(os.path.dirname(filename))
    if os.path.isdir(filename):
        # BUG... I don't know why this happens
        return
    with open(filename, 'wb') as code:
        code.write(r.content)


def user_in_database(username):
    # Returns True iff username is in the database
    payload = {'username': username}
    r = requests.get(SERVER_ADDRESS + 'user_in_database', data=payload)
    return r.content == TRUE


def view_all_files():
    """Returns information about files uploaded to the server"""
    payload = add_auth({})
    r = requests.get(SERVER_ADDRESS + 'view_all_files', data=payload)
    return r.content


def view_user_files(viewUser):
    """Returns information about files uploaded to the server by a specific user"""
    payload = {'viewUser': viewUser}
    payload = add_auth(payload)
    r = requests.get(SERVER_ADDRESS + 'view_user_files', data=payload)
    return r.content

# Client-side state manipulation
###########


def change_directory(dirname):
    """Changes the user's OneDir directory to directory specified by dirname"""
    sync(False)
    sess = session()
    username = sess['username']
    ONEDIR_DIRECTORY = read_config_file(username)
    shutil.move(ONEDIR_DIRECTORY, dirname)
    write_config_file(dirname, username)
    sync(True)


def quit_session():
    """Logs the user out"""
    sess = session()
    if sess['sync'] == '1':
        sync(False)
    payload = add_auth({})
    os.remove("/tmp/onedir.session")
    r = requests.post(SERVER_ADDRESS + 'logout', data=payload)
    if r.content == FALSE:
        print("You are not logged in on the server...")


def stop():
    """Stops the daemon that checks for file updates, and then logs the user out"""
    sync(False)
    quit_session()


def sync(on):
    # Run the daemon that checks for file updates and stuff
    if not DEBUG:
        sess = session()
        onedir_daemon = OneDirDaemon(PID_FILE, sess['username'])
        if on:
            onedir_daemon.start()
            sess['sync'] = '1'
        else:
            onedir_daemon.stop()
            sess['sync'] = '0'
        update_session(sess)
        return sess['sync'] == '1'
    else:
        sess = session()
        ONEDIR_DIRECTORY = read_config_file(sess['username'])
        t = pynotify_update.FileUpdateChecker(ONEDIR_DIRECTORY)
        if on:
            t.start()
            sess['sync'] = '1'
        else:
            t.stop()
            sess['sync'] = '0'
        update_session(sess)
        return sess['sync'] == '1'

# Configuration related functions
##########
order = ['username', 'auth', 'sync']


def parse_listing(listing, user=False):
    # takes either a username or the contents of a /listing request
    #  from the server.
    userhome = os.environ['HOME']
    listing_file = listing+".listing"
    listing_file = os.path.join(userhome, ".onedir", listing_file)
    if user:
        try:
            listing = open(listing_file, 'r').read()
        except:
            listing = ""
            open(listing_file, 'w').write("")

    # Split it down to the right format
    return [k.strip().split(' ') for k in listing.strip().split('\n') if k.strip() != ""]


def read_config_file(username):
    """Reads the config file to determine the user's preferences when the application is opened"""
    userhome = os.environ['HOME']
    config_path = os.path.join(userhome, ".onedir", username+".config")
    try:
        with open(config_path, 'r') as afile:
            return afile.readline()
    except Exception as e:
        print "Configuration file does not exist!"
        print e.message
        return False


def session():
    """Returns a list containing information about the current session (username, auth)"""
    try:
        session_file = open("/tmp/onedir.session", 'r').read().split("\n")
        session = {}
        for i in range(len(order)):
            session[order[i]] = session_file[i]

        return session
    except IOError:
        return False


def update_listings(username, path, timestamp, delete=False):
    userhome = os.environ['HOME']
    listing_file = username+".listing"
    listing = os.path.join(userhome, ".onedir", listing_file)
    l = []
    if os.path.isfile(listing):
        f = open(listing, 'r')
        l = f.readlines()
        f.close()
    found = False
    for k in range(len(l)):
        l[k] = l[k].strip().split(' ')
        if l[k][0] == path:
            if delete:
                found = k
            else:
                l[k][1] = str(timestamp)
                found = True
    if not found and not delete:
        l.append([path, str(timestamp)])
    if type(found) == int and delete:
        del l[found]
    f = open(listing, 'w')
    f.write('\n'.join([' '.join(k) for k in l]))
    f.close()


def update_session(session):
    """Updates the user's session file"""
    session_file = open("/tmp/onedir.session", 'w')
    for i in order:
        session_file.write(session[i] + '\n')
    session_file.close()


def write_config_file(onedir_path, username):
    """Writes a config file stored in the user's Home folder. This file allows user preferences to persist"""
    userhome = os.environ['HOME']
    folder = os.path.join(userhome, ".onedir")
    if not os.path.isdir(folder):
        os.makedirs(folder)
    config_file = username + ".config"
    config_path = os.path.join(folder, config_file)
    with open(config_path, 'w') as afile:
        afile.write(onedir_path)  # If we update the amount written, we need to update the amount read in read_config_file


# Misc Functions
#########


def add_auth(payload):
    """"Adds the auth value from session to a request before it is sent to the server"""
    sess = session()
    payload['username'] = sess['username']
    payload['auth'] = sess['auth']
    return payload


def get_file_paths(directory):
    """Recursively returns all the files stored in a directory"""
    file_paths = {}

    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths[filepath] = os.path.getmtime(filepath)

    return file_paths


def r_mkdir(dirname):
    """Recursively makes directories so they always exist before we try to save a file"""
    if os.path.exists(dirname):
        return
    else:
        r_mkdir(os.path.dirname(dirname))
        os.makedirs(dirname)
        print(dirname)


def sanity_check_username(name):
    """"Makes sure the user's input username is acceptable"""
    VALID_CHARACTERS = string.ascii_letters+string.digits+"_-."
    rules = [ 
        len(name) > 3,  # User name is longer than 3 characters
        all([k in VALID_CHARACTERS for k in list(name)])  # Username is made of valid characters
    ]
    return all(rules)


class OneDirDaemon(daemon.Daemon):
    """"Daemonizes the OneDir client so it can run in the background"""

    def __init__(self, pidfile, username):
        """Init function for daemon"""
        daemon.Daemon.__init__(self, pidfile)
        self.username = username

    def run(self):
        """Starts the daemon!"""
        ONEDIR_DIRECTORY = read_config_file(self.username)
        pynotify_update.FileUpdateChecker(ONEDIR_DIRECTORY).start()

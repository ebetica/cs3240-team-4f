# The non-interactive parts of the client
import string
import os
import requests 
import daemon
import pynotify_update
from constants import *
import shutil
import sys
from threading import Timer

DEBUG = False

# Server request related function
########

def user_in_database(username):
    # Returns True iff username is in the database
    payload = {'username': username}
    r = requests.get(SERVER_ADDRESS + 'user_in_database', data=payload)
    return r.content == TRUE

def register_user(username,password,email=None,_type='user'):
    if not user_in_database(username):
        if email is None:
            email=''
        if sanity_check_username(username):
            payload={'username':username, 'password': password, 'email': email, 'user_type':_type}
            r=requests.post(SERVER_ADDRESS + 'register', data=payload)
        else:
            pass
            #toss error or re-enter.
            
def login_user(username, password):
    payload = {'username': username, 'password': password}
    r = requests.post(SERVER_ADDRESS + 'login', data=payload)
    return r.content

def get_user_list():
    payload = {'value': 'username', 'table': 'users'}
    r = requests.get(SERVER_ADDRESS+'getVals', data=payload)
    return r.content

def upload_file(url, filename, timestamp):
    sess = session()
    ONEDIR_DIRECTORY = read_config_file(sess['username'])
    rel_path = os.path.relpath(filename, ONEDIR_DIRECTORY )
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
    if r.content == FALSE:
        print("You are not logged in! Shutting down OneDir...")
        quit_session()
    return r.status_code

def share_file(user,pathName):
    url = SERVER_ADDRESS + 'share'
    sess = session()
    username = sess['username']
    payload = add_auth({'ShareWith': user, 'PathName': pathName})
    r = requests.post(url, data=payload)
    return r.status_code


def download_file(url, filename):
    url += 'download/'
    url += filename
    payload = add_auth({})
    r = requests.get(url, data=payload)
    if r.content == FALSE:
        print("You are not logged in! Shutting down OneDir...")
        quit_session()
    if filename != "":
        filename = os.path.join(read_config_file(session()["username"]), filename)
        with open(filename, 'wb') as code:
            code.write(r.content)

def delete_file(url, filename):
    url += 'delete'
    sess = session()
    onedir_directory = read_config_file(sess['username'])
    rel_path = os.path.relpath(filename, onedir_directory)
    payload = add_auth({'rel_path':rel_path})
    r = requests.get(url, data=payload)
    if r.content == FALSE:
        print("You are not logged in! Shutting down OneDir...")
        quit_session()

def download_file_updates(url):
    url += 'sync'
    sess = session()
    payload = add_auth({})
    r = requests.get(url, data=payload)
    if r.content == FALSE:
        print("You are not logged in! Shutting down OneDir...")
        quit_session()
    with open('.onedirdata', 'wb') as code:
        code.write(r.content)

def file_listing():
    url = SERVER_ADDRESS
    url += 'listing'
    sess = session()
    payload = add_auth({})
    r = requests.get(url, data=payload)
    if r.content == FALSE:
        print("You are not logged in! Shutting down OneDir...")
        quit_session()
    listing = [k.split(' ') for k in r.content.split('\n')]
    return listing

def check_updates():
    url = SERVER_ADDRESS
    ONEDIR_DIRECTORY = read_config_file(session()['username'])
    server_listing = file_listing()
    server_files = {}
    local_listing = get_file_paths(ONEDIR_DIRECTORY)
    for afile in server_listing:
        afile = afile.split(' ')
        filename = afile[0]
        server_files[filename] = afile[1]
        if filename not in local_listing:
            download_file(url, filename)
    for afile in local_listing:
        if afile not in server_files.keys():
            upload_file(url, afile, os.path.getmtime(afile))
        elif server_files[afile] < os.path.getmtime(afile):
            upload_file(url, afile, os.path.getmtime(afile))

def reset_password(username):
    payload = {'username': username}
    r = requests.post(SERVER_ADDRESS + 'reset_password', data=payload)
    return r.content == TRUE

def change_password(oldpass, newpass):
    sess = session()
    payload = {'username': sess['username'], 'oldpass': oldpass, 'newpass': newpass}
    r = requests.post(SERVER_ADDRESS + 'password_change', data=payload)
    return r.content == TRUE

def remove_user(username):
    payload = {'username': username}
    r = requests.post(SERVER_ADDRESS + 'remove_user', data = payload)
    return r.content == TRUE

def is_admin(username):
    payload = {'username': username}
    r = requests.get(SERVER_ADDRESS + 'user_is_admin', data=payload)
    return r.content == TRUE

def view_user_files(username):
    payload = {'username': username}
    r = requests.get(SERVER_ADDRESS + 'view_user_files', data=payload)
    return r.content

def view_all_files():
    payload = {}
    r = requests.get(SERVER_ADDRESS + 'view_all_files', data = payload)
    return r.content





# Client-side state manipulation
###########

def change_directory(dirname):
    sess = session()
    username = sess['username']
    ONEDIR_DIRECTORY = read_config_file(username)
    shutil.move(ONEDIR_DIRECTORY, dirname)
    write_config_file(dirname, username)
    sync(False)
    sync(True)

def quit_session():
    sess = session()
    if sess['sync'] == '1':
        sync(False)
    payload = add_auth({})
    os.remove("/tmp/onedir.session")
    r = requests.post(SERVER_ADDRESS + 'logout', data=payload)
    if r.content == FALSE:
        print("You are not logged in on the server...")

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
        return sess['sync']  == '1'
    else:
        sess = session()
        ONEDIR_DIRECTORY = read_config_file(sess['username'])
        t = Timer(1, check_updates()) #This should be accessible from other methods
        if on:
            t.start() #If it's accessible from other methods, it's easy to stop fuc.stop() BOOM!
            sess['sync'] = '1'
        else:
            t.stop()
            sess['sync'] = '0'
        update_session(sess)
        return sess['sync']  == '1'

def stop():
    sync(False)
    quit_session()



# Configuration related functions
##########

order = ['username', 'auth', 'sync']
def session():
    try:
        session_file = open("/tmp/onedir.session", 'r').read().split("\n")
        session = {}
        for i in range(len(order)):
            session[order[i]] = session_file[i]

        return session
    except IOError:
        return False
    
def update_session(session):
    session_file = open("/tmp/onedir.session", 'w')
    for i in order:
        session_file.write(session[i] + '\n')
    session_file.close()


def write_config_file(onedir_path, username):
    userhome = os.environ['HOME']
    config_file = '.onedirconfig_' + username
    config_path = os.path.join(userhome, config_file)
    with open(config_path, 'w') as afile:
        afile.write(onedir_path) #If we update the amount written, we need to update the amount read in read_config_file
    return True

def read_config_file(username):
    userhome = os.environ['HOME']
    config_file = '.onedirconfig_' + username
    config_path = os.path.join(userhome, config_file)
    try:
        with open(config_path, 'r') as afile:
            return afile.readline()
    except Exception as e:
        print e.message
        return False



# Misc Functions
#########

def get_file_paths(directory):
    file_paths = {}

    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths[filepath] = os.path.getmtime(filepath)

    return file_paths

def sanity_check_username(name):
    VALID_CHARACTERS = string.ascii_letters+string.digits+"_-."
    rules = [ 
            len(name) > 3, # User name is longer than 3 characters
            all([k in VALID_CHARACTERS for k in list(name)]) # Username is made of valid characters
            ]
    return all(rules)

def add_auth(payload):
    sess = session()
    payload['username'] = sess['username']
    payload['auth'] = sess['auth']
    return payload

class OneDirDaemon(daemon.Daemon):
    def __init__(self, pidfile, username):
        daemon.Daemon.__init__(self, pidfile)
        self.username = username

    def run(self):
        sys.stderr.write("Hi")
        ONEDIR_DIRECTORY = read_config_file(self.username)
        pynotify_update.FileUpdateChecker(ONEDIR_DIRECTORY).start()

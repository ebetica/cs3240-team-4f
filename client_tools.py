# The non-interactive parts of the client
import string, os
import requests 
import daemon
import pynotify_update
from constants import *

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
    payload={'item': 'username'}
    r=requests.get(SERVER_ADDRESS+'getVals',data=payload)

def sanity_check_username(name):
    VALID_CHARACTERS = string.ascii_letters+string.digits+"_-."
    rules = [ 
            len(name) > 3, # User name is longer than 3 characters
            all([k in VALID_CHARACTERS for k in list(name)]) # Username is made of valid characters
            ]
    return all(rules)

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

def change_directory(dirname):
    sess = session()
    username = session['username']
    ONEDIR_DIRECTORY = read_config_file(username)
    shutil.move(ONEDIR_DIRECTORY, dirname)
    write_config_file(dirname, username)

def upload_file(url, filename):
    url += 'upload'
    sess = session()
    payload = {'username': sess['username'], 'hash': sess['auth']}
    files = {'file': open(filename, 'rb')}
    r = requests.post(url, files=files, data=payload)
    return r.status_code


def download_file(url, filename):
    url += 'uploads/'
    url += filename
    sess = session()
    payload = {'username': sess['username'], 'hash': sess['auth']}
    r = requests.get(url, data=payload)
    with open(filename, 'wb') as code:
        code.write(r.content)

def download_file_updates(url):
    url += 'sync'
    sess = session()
    payload = {'username': sess['username'], 'hash': sess['auth']}
    r = requests.get(url, data=payload)
    with open('.onedirdata', 'wb') as code:
        code.write(r.content)

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

def session():
    order = ['username', 'auth', 'sync']
    try:
        session_file = open("/tmp/onedir.session", 'r').read().split("\n")
        session = {}
        for i in range(len(order)):
            session[order[i]] = session_file[i]

        return session
    except IOError:
        return False
    
def update_session(session):
    order = ['username', 'auth', 'sync']
    session_file = open("/tmp/onedir.session", 'w')
    for i in order:
        session_file.write(session[i] + '\n')
    session_file.close()

def quit_session():
    os.remove("/tmp/onedir.session")

class OneDirDaemon(daemon.Daemon):
    def __init__(self, pidfile, username):
        daemon.Daemon.__init__(self, pidfile)
        self.username = username

    def run(self):
    # Run the daemon that checks for file updates and stuff
        ONEDIR_DIRECTORY = read_config_file(self.username)
        fuc = pynotify_update.FileUpdateChecker(ONEDIR_DIRECTORY)  #This should be accessible from other methods
        fuc.start() #If it's accessible from other methods, it's easy to stop fuc.stop() BOOM!

def sync(on):
    # Run the daemon that checks for file updates and stuff
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

def stop():
    sync(False)
    quit_session()



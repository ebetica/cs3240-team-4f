# The non-interactive parts of the client
import string
import requests 
from constants import *
import os

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
            	string = afile.readline()
		return string
    except Exception as e:
        print e.message
        return False


def upload_file(url, filename):
    url += 'upload'
    sess = session()
    payload = {'username': sess['username'], 'hash': sess['auth']}
    files = {'file': open(filename, 'rb')}
    r = requests.post(url, files=files, data=payload)
    return r.status_code


def download_file(url, filename):
    url += 'uploads/server.py'
    session = session()
    payload = {'username': session['username'], 'hash': session['auth']}
    r = requests.get(url, data=payload)
    with open(filename, 'wb') as code:
        code.write(r.content)

def reset_password(username):
    payload = {'username': username}
    r = requests.post(SERVER_ADDRESS + 'reset_password', data=payload)
    return r.content == TRUE

def remove_user(username):
    payload = {'username': username}
    r = requests.post(SERVER_ADDRESS + 'remove_user', data = payload)
    return r.content == TRUE

def update_session(session):
    order = ['username', 'auth', 'sync']
    session_file = open("/tmp/onedir.session", 'w')
    for i in order:
        session_file.write(session[i] + '\n')
    session_file.close()

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
    

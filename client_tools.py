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

def register_user(username,password,email=None):
    if not user_in_database(username):
        if email is None:
            email=''
        if sanity_check_username(username):
            payload={'username':username, 'password': password, 'email': email}
            r=requests.post(SERVER_ADDRESS + 'register', data=payload)
        else:
            pass
            #toss error or re-enter.
            
def login_user(username, password):
    payload = {'username': username, 'password': password}
    r = requests.post(SERVER_ADDRESS + 'login', data=payload)
    return r.content == TRUE


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
    if not os.path.isfile(config_path):
        with open(config_path, 'w') as afile:
            afile.write(onedir_path)
        return True
    else:
        #Flip out!!!! THE FILE ALREADY EXISTS!!!*!*!*!
        return False

def upload_file(url, filename):
    url += 'upload'
    files = {'file': open(filename, 'rb')}
    r = requests.post(url, files=files)


def download_file(url, filename):
    url += 'uploads/server.py'
    r = requests.get(url)
    with open(filename, 'wb') as code:
        code.write(r.content)
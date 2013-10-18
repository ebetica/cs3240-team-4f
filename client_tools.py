# The non-interactive parts of the client
import string
import requests 
from constants import *

def user_in_database(username):
    # Returns True iff username is in the database
    payload = {'username': username}
    r = requests.get(SERVER_ADDRESS + 'user_in_database', data=payload)
    return r.content == TRUE


def register_user(username):
    # Asks for password and relevent information and registers user.
    pass


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

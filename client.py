import client_tools
import os
import sys
import argparse
import pynotify_update
import shutil
from constants import *

__author__ = 'robert'

#Contains the code for Team 18's dropbox client
#This is only for methods that directly prompt the user for input

def parse_user():
    #prompt for username
    #check user name isn't in db already
    #add user to db
    #returns the hash that authenticates the user for the session
    username = raw_input("Username: ")
    while not client_tools.sanity_check_username(username):
        username = raw_input("Username: ")
    in_database = client_tools.user_in_database(username)
    loggedin = False
    if in_database:
        # User is in database
        password = raw_input("Password: ")
        h = client_tools.login_user(username, password)
        while h == FALSE:
            password = raw_input("Wrong password, try again: ")
            h = client_tools.login_user(username, password)
    else:
        h = make_new_user(username)
    return (username, h)

def make_new_user(username):
    # Get password and email
    print("New user! Please enter your password below:")
    password = raw_input("Password: ")
    email = raw_input("Email: ")
    user_type = raw_input("Admin or User: ")
    print('Please enter the directory you would like to keep synced with the OneDir service.')
    print('A blank directory will default to ~/OneDir/')
    directory = raw_input("Directory: ")
    if directory == "":
        ONEDIR_DIRECTORY = os.path.join(os.environ['HOME'], 'OneDir')
        client_tools.write_config_file( ONEDIR_DIRECTORY, username)
    else:
        client_tools.write_config_file(directory, username)
    client_tools.register_user(username, password, email, user_type)
    h = client_tools.login_user(username, password)
    return h

def change_password():
    # Prompt for the password and change it
    pass

def reset_password():
    # are we prompting admins for pw before big changes
    # print("Admin password reset. Please enter your password below:")
    #password = raw_input("")
    sess = client_tools.session()
    print("Reset password.")
    if client_tools.is_admin(sess['username']):
        print("Please enter the user to reset the password for.")
        user = raw_input("Username:")
        client_tools.reset_password(user)
    else:
        if raw_input("Are you sure? (Y/N)").capitalize() in ['Y', 'YES']:
            client_tools.reset_password(sess['username'])


def remove_user():
    sess = client_tools.session()
    print("Removing user")
    if client_tools.is_admin(sess['username']):
        print("Please enter the user to remove.")
        user = raw_input("Username:")
        client_tools.remove_user(user)

def sync(on):
    # Run the daemon that checks for file updates and stuff
    sess = client_tools.session()
    ONEDIR_DIRECTORY = client_tools.read_config_file(sess['username'])
    fuc = pynotify_update.FileUpdateChecker(ONEDIR_DIRECTORY)
    fuc.start()
    if on:
        fuc.start()
        return True
    else:
        fuc.stop()
        return False

def change_directory(dirname):
    username = ''  #We should get the username. Otherwise I'll be unhappy
    ONEDIR_DIRECTORY = client_tools.read_config_file(username)
    shutil.move(ONEDIR_DIRECTORY, dirname)
    client_tools.write_config_file(dirname, username)

def ExistingUsers():
    print client_tools.get_user_list(); 

def main():
    parser = argparse.ArgumentParser(description=
    '''OneDir is a wonderful program. Run it without any arguments to simply start the client''')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-p", "--change-password", action="store_true",
            help="Open a prompt to change your password")
    group.add_argument("-c", "--sync", action="store_true",
            help="Set sync on")
    group.add_argument("-n", "--no-sync", action="store_true",
            help="Set sync off")
    group.add_argument("-s", "--stop", action="store_true",
            help="STOP THE PRESS (client)")
    group.add_argument("-d", "--change-directory", type=str,
            help="Change the default directory of OneDir")
    args = parser.parse_args()
    # Throw an error if OneDir is not running!
    if client_tools.session():
        if args.change_password:
            change_password()
        elif args.sync:
            sync(True)
        elif args.no_sync:
            sync(False)
        elif args.change_directory:
            change_directory(args.change_directory)
        else:
            print("OneDir is already running!")
    else:
        # No options are passed in, so just start the program
        if len(sys.argv) == 1:
            print("Starting OneDir...")
            username, h = parse_user()
            session = {}
            session['username'] = username
            session['auth'] = h
            session['sync'] = '1'
            client_tools.update_session(session)
            success = sync(True)

if __name__ == '__main__':
    main()

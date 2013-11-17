import os, sys, argparse
from constants import *
import client_tools
import shutil

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
    print("Change password.")
    if raw_input("Are you sure? (Y/N)").capitalize() in ['Y', 'YES']:
        oldpass = raw_input("Old password: ")
        pass1 = raw_input("New password: ")
        pass2 = raw_input("Re-enter new password: ")
        if pass1 == pass2:
            success = client_tools.change_password(oldpass, pass1)
            if not success:
                print("Wrong old password, try again:(")
                change_password()
        else:
            print("Passwords did not match")
            change_password()

def reset_password():
    sess = client_tools.session()
    print("Reset password.")
    if client_tools.is_admin(sess['username']):
        print("Please enter the user to reset the password for.")
        user = raw_input("Username: ")
        client_tools.reset_password(user)
    else:
        if raw_input("Are you sure? (Y/N)").capitalize() in ['Y', 'YES']:
            client_tools.reset_password(sess['username'])

def view_user_files():
    sess = client_tools.session()
    if client_tools.is_admin(sess['username']):
        print("Please enter the user to view the file sizes and counts for.")
        user = raw_input("Username: ")
        sizes = client_tools.view_user_files(user)
        print("File number: " + sizes[1])
        print(sizes[0])

def view_all_files():
    sess = client_tools.session()
    if client_tools.is_admin(sess['username']):
        sizes = client_tools.view_all_files()
        print("File number: " + sizes[1])
        print(sizes[0])


def remove_user():
    sess = client_tools.session()
    print("Removing user")
    if client_tools.is_admin(sess['username']):
        print("Please enter the user to remove.")
        user = raw_input("Username: ")
        client_tools.remove_user(user)
def share_file():
    user= raw_input("Username of who to share with: ")
    pathName=raw_input("Enter Full Path to File: ")
    client_tools.share_file(user,pathName)

def ExistingUsers():
    sess = client_tools.session()
    print("User list")
    if client_tools.is_admin(sess['username']):
        print client_tools.get_user_list();

def main():
    parser = argparse.ArgumentParser(description=
    '''OneDir is a wonderful program. Run it without any arguments to simply start the client''')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-p", "--change-password", action="store_true",
            help="Open a prompt to change your password")
    group.add_argument("-s", "--sync", action="store_true",
            help="Set sync on")
    group.add_argument("-n", "--no-sync", action="store_true",
            help="Set sync off")
    group.add_argument("-q", "--stop", "--quit", action="store_true",
            help="STOP THE PRESS (client)")
    group.add_argument("-d", "--change-directory", type=str,
            help="Change the default directory of OneDir")
    args = parser.parse_args()
    # Throw an error if OneDir is not running!
    if client_tools.session():
        if args.change_password:
            change_password()
        elif args.sync:
            client_tools.sync(True)
        elif args.no_sync:
            client_tools.sync(False)
        elif args.change_directory:
            client_tools.change_directory(args.change_directory)
        elif args.stop:
            client_tools.stop()
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
            client_tools.sync(True)
            print("OneDir is now running!")

if __name__ == '__main__':
    main()

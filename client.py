import client_tools
from constants import *

import argparse
import os
import sys

#Contains the code for Team 18's dropbox client
#This is only for methods that directly prompt the user for input


def change_password():
    """Prompts user for information to change password"""
    print("Change password.")
    if raw_input("Are you sure? (Y/N)").capitalize() in ['Y', 'YES']:
        oldpass = raw_input("Old password: ")
        pass1 = raw_input("New password: ")
        pass2 = raw_input("Re-enter new password: ")
        if pass1 == pass2:
            success = client_tools.password_change(oldpass, pass1)
            if not success:
                print("Wrong old password, try again:(")
                change_password()
        else:
            print("Passwords did not match")
            change_password()


def get_user_list():
    """Returns a list of all users registered for the OneDir service"""
    sess = client_tools.session()
    print("User list")
    if client_tools.is_admin(sess['username']):
        print client_tools.get_user_list()
    else:
        print("Please login as an admin user")


def make_new_user(username):
    """Get password and email to create a new user"""
    print("New user! Please enter your password below:")
    password = raw_input("Password: ")
    email = raw_input("Email: ")
    user_type = raw_input("Admin or User: ")
    print('Please enter the directory you would like to keep synced with the OneDir service.')
    print('A blank directory will default to ~/OneDir/')
    directory = raw_input("Directory: ")
    if directory == "":
        directory = os.path.join(os.environ['HOME'], 'OneDir')
    client_tools.write_config_file(directory, username)
    h = client_tools.login_user(username, password)
    return h


def parse_user():
    #prompt for username
    #check user name isn't in db already
    #add user to db
    #returns the hash that authenticates the user for the session
    username = raw_input("Username: ")
    while not client_tools.sanity_check_username(username):
        username = raw_input("Username: ")
    in_database = client_tools.user_in_database(username)
    if in_database:
        # User is in database
        password = raw_input("Password: ")
        h = client_tools.login_user(username, password)
        while h == FALSE:
            # Password is wrong!
            password = raw_input("Wrong password, try again: ")
            h = client_tools.login_user(username, password)
        if not client_tools.read_config_file(username):
            # No config file currently exists for the given user :(
            print('Please enter the directory you would like to keep synced with the OneDir service.')
            print('A blank directory will default to ~/OneDir/')
            directory = raw_input("Directory: ")
            if directory == "":
                directory = os.path.join(os.environ['HOME'], 'OneDir')
            client_tools.write_config_file(directory, username)
    else:
        h = make_new_user(username)
    return (username, h)


def remove_user():
    sess = client_tools.session()
    print("Removing user")
    if client_tools.is_admin(sess['username']):
        print("Please enter the user to remove.")
        user = raw_input("Username: ")
        client_tools.remove_user(user)
    else:
        print("Please login as an admin user")


def reset_password():
    """Resets the password for entered user"""
    sess = client_tools.session()
    print("Reset password.")
    if client_tools.is_admin(sess['username']):
        print("Please enter the user to reset the password for.")
        user = raw_input("Username: ")
        client_tools.password_reset(user)
    else:
        if raw_input("Are you sure? (Y/N)").capitalize() in ['Y', 'YES']:
            client_tools.password_reset(sess['username'])


def share_file():
    """Prompts user for information to share a file with another user"""
    user = raw_input("Username of user to share with: ")
    pathName = raw_input("Enter full path to File: ")
    client_tools.share_file(user, pathName)


def view_all_files():
    """Allows user to view information about all files stored on the OneDir server"""
    sess = client_tools.session()
    if client_tools.is_admin(sess['username']):
        sizes = str.split(client_tools.view_all_files(), ',')
        print(sizes[1] + ' files')
        print(sizes[0] + ' bytes used')
    else:
        print("Please login as an admin user")


def view_user_files():
    """Allows user to view information about all files stored by one user on the OneDir server"""
    sess = client_tools.session()
    if client_tools.is_admin(sess['username']):
        print("Please enter the user to view the file sizes and counts for.")
        user = raw_input("Username: ")
        sizes = str.split(client_tools.view_user_files(user), ',')
        print(sizes[1] + ' files')
        print(sizes[0] + ' bytes used')
    else:
        print("Please login as an admin user")

def delete_user_files():
    sess = client_tools.session()
    if client_tools.is_admin(sess['username']):
        print("Please enter the user to delete files from.")
        user = raw_input("Username: ")
        print("Please enter the file name to delete.")
        filename = raw_input("Filename: ")
        client_tools.delete_user_files(user, filename)
    else:
        print("Please login as an admin user")

def main():
    parser = argparse.ArgumentParser(description=
                                     '''OneDir is a wonderful program. Run without any arguments to start the client''')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-p", "--change-password", action="store_true",
                       help="Open a prompt to change your password")
    group.add_argument("-r", "--reset-password", action="store_true",
                       help="Open a prompt to reset a user's password (admin only)")
    group.add_argument("-s", "--sync", action="store_true",
                       help="Set sync on")
    group.add_argument("-n", "--no-sync", action="store_true",
                       help="Set sync off")
    group.add_argument("-q", "--stop", "--quit", action="store_true",
                       help="STOP THE PRESS (client)")
    group.add_argument("-d", "--change-directory", type=str,
                       help="Change the default directory of OneDir")
    group.add_argument("-f", "--share-file", action="store_true",
                       help="Share a file with another OneDir user")
    group.add_argument("-l", "--list-users", action="store_true",
                       help="List all users (admin only)")
    group.add_argument("-u", "--view-user-files", action="store_true",
                       help="View information about a user's files (admin only)")
    group.add_argument("-a", "--view-all-files", action="store_true",
                       help="View information about all files store on the server (admin only)")
    args = parser.parse_args()
    # Throw an error if OneDir is not running!
    if client_tools.session():
        if args.change_password:
            change_password()
        elif args.reset_password:
            reset_password()
        elif args.sync:
            client_tools.sync(True)
        elif args.no_sync:
            client_tools.sync(False)
        elif args.change_directory:
            client_tools.change_directory(args.change_directory)
        elif args.share_file:
            share_file()
        elif args.list_users:
            get_user_list()
        elif args.view_user_files:
            view_user_files()
        elif args.view_all_files:
            view_all_files()
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

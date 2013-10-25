import client_tools
import os

__author__ = 'robert'

#Contains the code for Team 18's dropbox client
#This is only for methods that directly prompt the user for input

def parse_user():
    #prompt for username
    #check user name isn't in db already
    #add user to db
    username = raw_input("Username: ")
    while not client_tools.sanity_check_username(username):
        username = raw_input("Username: ")
    in_database = client_tools.user_in_database(username)
    loggedin = False
    if in_database:
        # User is in database
        password = raw_input("Password: ")
        loggedin = client_tools.login_user(username, password)
    else:
        make_new_user(username)
    return (username, loggedin)

def make_new_user(username):
    # Get password and email
    print("New user! Please enter your password below:")
    password = raw_input("Password: ")
    email = raw_input("Email: ")
    print('Please enter the directory you would like to keep synced with the OneDir service.')
    print('A blank directory will default to ~/OneDir/')
    directory = raw_input("Directory: ")
    loggedin = client_tools.register_user(username, password, email)


def main():
    parse_user()

if __name__ == '__main__':
    main()

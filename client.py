import client_tools
import os

__author__ = 'robert'

#Contains the code for Team 18's dropbox client

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
        # Get password and email
        print("New user! Please enter your password below:")
        password = raw_input("Password: ")
        email = raw_input("Email: ")
        loggedin = client_tools.register_user(username, password, email)
    return (username, loggedin)

def write_config_file(onedir_path, username):
    userhome = os.environ['HOME']
    config_file = '.onedirconfig' + username
    config_path = os.path.join(userhome, config_file)
    if not os.path.isfile(config_path):
        with open(config_path, 'w') as afile:
            afile.write(onedir_path)
        return True
    else:
        #Flip out!!!! THE FILE ALREADY EXISTS!!!*!*!*!
        return False

def main():
    parse_user()

if __name__ == '__main__':
    main()

import os
import client_tools
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
        password = ""
        email = ""
        loggedin = client_tools.register_user(username, password, email)
    return (username, loggedin)

def create_user_directory():
    # prompt user for home directory location
    # return the locaton
    pass

def initiate_config_file(config_file, initial_dir):
    pass

def main():
    filename = os.path.expanduser("~/.onedirc")
    config = None
    new_user = False #A user is new if they haven't registered
    try:
        config = open(filename, 'r')
    except IOError:
        # We don't want to go around creating random files yet
        # config = open(filename, 'w')
        new_user = True
    #check for config file at user's home directory (start it with . to be hidden)
    #if doesn't exist prompt user to login or register
    if new_user:
        username, sucess = parse_user()
        dirname = create_user_directory()
        initiate_config_file(config, dirname)
    else:
        #read config file
        #start syncing files, client should persist (not sprint 1 work)
        pass
    config.close()

if __name__ == '__main__':
    main()

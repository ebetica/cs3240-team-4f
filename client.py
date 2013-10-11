import os
import flask
__author__ = 'robert'

#Contains the code for Team 18's dropbox client


def db_connect():
    #code for database connection goes here
    pass


def add_user(name):
    #code for adding a user to the database goes here
    #
    pass


def create_new_user():
    #prompt for username
    #check user name isn't in db already
    #add user to db
    pass


def create_user_directory():
    # prompt user for home directory location
    # return the location
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
        config = open(filename, 'w')
        new_user = True
    #check for config file at user's home directory (start it with . to be hidden)
    #if doesn't exist prompt user to login or register
    if new_user:
        create_new_user()
        dirname = create_user_directory()
        initiate_config_file(config, dirname)
    else:
        #read config file
        #start syncing files, client should persist (not sprint 1 work)
        pass

if __name__ == '__main__':
    main()

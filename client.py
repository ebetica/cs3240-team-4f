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
    pass


def main():
    #check for config file at user's home directory (start it with . to be hidden)
    new_user = False #A user is new if they don't have this config file
    if new_user:
        create_new_user()
        create_user_directory()
    else:
        #read config file
        #start syncing files, client should persist (not sprint 1 work)
        pass

if __name__ == '__main__':
    main()
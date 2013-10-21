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


def main():
    parse_user()


if __name__ == '__main__':
    main()

import server

import hashlib
import os
import random
import string


def login(username, password):
    """Logs a user in to the OneDir server. Helper method for several methods in server.py"""
    user = server.query_db("SELECT * FROM users WHERE username=?", [username], one=True)
    if user is None:
        return False
    userval = user[1]
    progval = password_hash(password + user[2])
    if user[1] == password_hash(password + user[2]):
        letters = string.ascii_letters+string.digits
        h = ''.join([random.choice(letters) for k in range(20)])
        return (user, h)
    else:
        return False


def password_hash(password):
    """Returns a hex format hash of the input password. Input password should contain salt already."""
    return hashlib.sha1(password).hexdigest()


def r_mkdir(dirname):
    """Recursively makes directories so they always exist before we try to save a file"""
    if os.path.exists(dirname):
        return
    else:
        r_mkdir(os.path.dirname(dirname))
        os.makedirs(dirname)
        print(dirname)


def safeHashFile(path):
    """Safe way to hash large files (reads and hashes in chunks)"""
    #From www.pythoncentral.io/hashing-files-with-python/
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(path, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


def scrub_sqlite_input(table_name):
    """Sanitizes input to SQL queries to prevent SQL injection attacks"""
    return ' '.join(char for char in table_name if char.isalnum())


def update_listings(listing, path, timestamp, auth, delete=False):
    """Updates the specified listing file with a new line containing the filename, timestamp and user auth code"""
    l = []
    if os.path.isfile(listing):
        f = open(listing, 'r')
        l = f.readlines()
        f.close()
    found = False
    for k in range(len(l)):
        l[k] = l[k].strip().split(' ')
        if l[k][0] == path:
            if delete:
                found = k
            else:
                l[k][1] = str(timestamp)
                l[k][2] = auth
                found = True
    if not found and not delete:
        l.append([path, timestamp, auth])
    print("Found = %d" % (found))
    if type(found) == int and delete:
        del l[found]
    print l
    f = open(listing, 'w')
    f.write('\n'.join([' '.join(k) for k in l]))
    f.close()


def user_in_database(username):
    """Checks if a user is in the OneDir database"""
    user = server.query_db("SELECT * FROM users WHERE username=?", [username], one=True)
    if user is not None:
        ret = True
    else:
        ret = False
    return ret


def user_is_admin(username):
    """Returns if a user is an admin user or just a normal user"""
    user_type = server.query_db("SELECT role FROM users WHERE username=?", [username], one=True)
    user_string = user_type[0]
    if str(user_string).lower() == 'user':
        ret = False
    else:
        ret = True
    return ret


def view_files(path):
    """Returns the size and number of files stored in a directory on the server"""
    file_sizes = 0
    file_number = 0
    for roots, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(roots, f)
            file_sizes += os.path.getsize(fp)
            file_number += 1
    files = [str(file_sizes), str(file_number)]
    string = ','.join(files)
    return string
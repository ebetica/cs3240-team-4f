__author__ = 'robert'


import hashlib
import os
import pickle
import random
import server
import string

#Safe way to hash large files (reads and hashes in chunks)
#From www.pythoncentral.io/hashing-files-with-python/
def safeHashFile( path):
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(path, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()

def scrub_sqlite_input(table_name):
    return ' '.join( chr for chr in table_name if chr.isalnum() )
#Builds a dictionary of the local files on the machine
#Uses filename as key, and stores an md5 hash of each file as well as when the file was last modified
def get_local_files(fileOb):
    fileDict = {}
    for root, dirs, files in os.walk(fileOb, topdown=False):
        for name in files:
            if not name == '.onedirdata':
                path = os.path.join(root, name)
                fileDict[name] = [safeHashFile(path), os.path.getmtime(path)]
        for name in dirs:
            fileDict.update(get_local_files(name))
    return fileDict

def build_file_listing( path):
    pick = get_local_files(path)
    print pick
    pickle_path = os.path.join(path ,'.onedirdata.p')
    with open(pickle_path, 'wb') as pickle_file:
        pickle.dump(pick, pickle_file)


def password_hash(password):
    # Make this return the proper hashed version later
    # Probably use SHA1 with salt
    return hashlib.sha1(password).hexdigest()

def user_in_database(username):
    user = server.query_db("SELECT * FROM users WHERE username=?", [username], one=True )
    if user is not None:
        ret = True
    else:
        ret = False
    return ret

def user_is_admin(username):
    user_type = server.query_db("SELECT role FROM users WHERE username=?", [username], one=True )
    if user_type == 'user':
        ret = False
    else:
        ret = True
    return ret

def login(username, password):
    user = server.query_db("SELECT * FROM users WHERE username=?", [username], one=True )
    if user is None: return False
    if user[1] == password_hash(password + user[2]):
        letters = string.ascii_letters+string.digits
        h = ''.join([random.choice( letters ) for k in range(20)])
        return (user,h)
    else:
        return False

def r_mkdir(dirname): 
    if os.path.exists(dirname):
        return
    else:
        r_mkdir(os.path.dirname(dirname))
        os.makedirs(dirname)
        print(dirname)

def update_listings(listing, path, timestamp, auth, delete=False):
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
    print("Found = %d"%(found))
    if type(found) == int and delete:
        del l[found]
    print l
    f = open(listing, 'w')
    f.write('\n'.join([' '.join(k) for k in l]))
    f.close()

def view_files(path):
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
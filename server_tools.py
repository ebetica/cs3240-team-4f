__author__ = 'robert'

import os
import hashlib
import pickle

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

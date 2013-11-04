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

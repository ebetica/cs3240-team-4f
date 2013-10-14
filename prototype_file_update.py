__author__ = 'robert'

import pickle
import hashlib
import os

def check_directory(path):
    if not os.path.isdir(path):
        os.mkdir(path)
        return False
    return True

def get_local_files(path):
    filelist = os.listdir(path)
    dict = {}
    for file in filelist:
        if os.path.isfile(file):
            dict += {file, [hashlib.md5(open(file, 'rb')).hexdigest(), os.path.getmtime(file)]}
        else:
            dict += get_local_files(path)
    return dict

def load_server_files(path):
    path = path + '/.onedirdata.p'
    if os.path.isfile(path):
        return pickle.load(open(path))
    else:
        return {}

def get_server_files():
    path = ''
    #get_update_files(server, username)
        #build path on server from username
        #downloads manifest of user files on server to $ONEDIR/.onedirdata.p
    return load_server_files(path)

def compareManifests(local, server):
    dict= {}
    serverUpdates = []
    localUpdates = []
    for filename in local.keys():
        if filename in server.keys():
            if not local[filename][0] ==  server[filename][0]:
                if local[filename][1] > server[filename][1]:
                    serverUpdates.add(filename)
                elif local[filename][1] < server[filename][1]:
                    localUpdates.add(filename)
        else:
            serverUpdates.add(filename)
    for filename in server.keys():
        if not filename in local.keys():
            localUpdates.add(filename)
    return [localUpdates, serverUpdates]

def check_updates(path):
    localManifest = get_local_files()
    serverManifest = get_server_files()
    return compareManifests(localManifest, serverManifest)


def main():
    pathname = '/home/robert/.onedir'
    if check_directory(pathname):
        updateFiles = check_updates(pathname)
        localUpdates = updateFiles[0]
        serverUpdates = updateFiles[1]

    else:
        updateFiles = get_server_files()


if __name__== '__main__':
    main()
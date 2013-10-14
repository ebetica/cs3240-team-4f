__author__ = 'robert'

import pickle
import hashlib
import os

#Prototype to compare files on disk to those stored on a server
#Download listing of files on server -> create listing of files on local machine -> compare listings -> update necessary files

#Makes sure the onedir directory exists on the local machine
#If it doesn't, this creates the directory and returns false
def check_directory(path):
    if not os.path.isdir(path):
        os.mkdir(path)
        return False
    return True

#Builds a dictionary of the local files on the machine
#Uses filename as key, and stores an md5 hash of each file as well as when the file was last modified
def get_local_files(path):
    filelist = os.listdir(path)
    dict = {}
    for file in filelist:
        if os.path.isfile(file):
            dict += {file, [hashlib.md5(open(file, 'rb')).hexdigest(), os.path.getmtime(file)]}
        else:
            dict += get_local_files(path)
    return dict

#Loads a dictionary of files stored on the server using pickle
def load_server_files(path):
    path = path + '/.onedirdata.p'
    if os.path.isfile(path):
        return pickle.load(open(path))
    else:
        return {}

#Connects to server, downloads a listing of the user's files and then returns that listing
def get_server_files():
    path = ''
    #get_update_files(server, username)
        #build path on server from username
        #downloads manifest of user files on server to $ONEDIR/.onedirdata.p
    return load_server_files(path)

#Compares the file listings between server and local machine
#Returns a list containing two lists
#The first list is a list of files that need to be updated on the local machine
#The second list is a list of files that need to be updated on the server
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

#Unifies above methods
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
    else: #Directory doesn't exist, so no local files are on machine
        serverUpdates = get_server_files()
    if localUpdates:
        #upload localUpdates
        pass
    if serverUpdates:
        #download serverUpdates
        pass


if __name__== '__main__':
    main()
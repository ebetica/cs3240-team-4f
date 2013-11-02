__author__ = 'robert'

import hashlib
import os
import pickle
import sys
import threading
import time
import client_tools
import constants


#Prototype to compare files on disk to those stored on a server
#Download listing of files on server -> create listing of files on local machine -> compare listings -> update necessary files
class ServerChecker(threading.Thread):
    path = ''  # path to Onedir directory
    interval = 5  # minutes between checking for updates


    def __init__(self, pathname, intervalIn):
        super(ServerChecker, self).__init__()
        userhome = os.environ['HOME']
        path = userhome + '/Onedir'
        if not pathname is None:
            self.path = pathname
        else:
            self.path = path
        if not intervalIn is None:
            self.interval = intervalIn

    #Makes sure the onedir directory exists on the local machine
    #If it doesn't, this creates the directory and returns false
    def check_directory(self):
        if not os.path.isdir(self.path):
            try:
                os.mkdir(self.path, 0700)
            except OSError:
                sys.exit( 'Cannot create onedir directory')
            return False
        return True

    #Safe way to hash large files (reads and hashes in chunks)
    #From www.pythoncentral.io/hashing-files-with-python/
    def safeHashFile(self, path):
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
    def get_local_files(self, fileOb):
        try:
            filelist = os.listdir(fileOb)
        except OSError:
            filelist = {}
        fileDict = {}
        for afile in filelist:
            if not afile == '.onedirdata.p':
                afile = (fileOb + '/' + afile)
                if os.path.isfile(afile):
                    fileDict[afile] = [self.safeHashFile(afile), os.path.getmtime(afile)]
                else:
                    fileDict.update(self.get_local_files(afile))
        return fileDict

    #Loads a dictionary of (files stored on the server) from Onedir directory using pickle
    def load_server_files(self):
        path = self.path + '/.onedirdata.p'  # Local machine path to dictionary of files from server
        if os.path.isfile(path):
            return pickle.load(open(path))
        else:
            return {}

    #Connects to server, downloads a listing of the user's files and then returns that listing
    def get_server_files(self):
        #get_update_files(server, username)
        #build path on server from username
        #downloads manifest of user files on server to $ONEDIR/.onedirdata.p
        return self.load_server_files()

    #Compares the file listings between server and local machine
    #Returns a list containing two lists
    #The first list is a list of files that need to be updated on the local machine
    #The second list is a list of files that need to be deleted from the local machine
    def compareManifests(self, local, server):
        localUpdates = []
        localDeletes = []
        for filename in local.keys():
            if filename in server.keys():
                if not local[filename][0] == server[filename][0]:
                    if local[filename][1] < server[filename][1]:
                        localUpdates.append(filename)  # add file to be updated on local machine
            # file exists locally, but not on server, though it previously was local. Should be deleted
            elif filename not in server.keys():
                localDeletes.append(filename)
        for filename in server.keys():
            # file was created elsewhere since last update; should be saved to local
            if (not filename in local.keys()):
                localUpdates.append(filename)  # add file to be updated on local machine
        return [localUpdates, localDeletes]

    #Unifies above methods
    def check_updates(self):
        localManifest = self.get_local_files(self.path)
        serverManifest = self.get_server_files()
        return self.compareManifests(localManifest, serverManifest)

    #runner for file updates
    def run_file_updates(self):

        if self.check_directory():
            updateFiles = self.check_updates()
            localUpdates = updateFiles[0]
            localDeletes = updateFiles[1]
        else:  # Directory doesn't exist, so no local files are on machine
            localDeletes = []  # No local files on machine means no updates need to be made to server
            localUpdates = self.get_server_files()  # Local machine needs all files from server
        if localUpdates:
            for afile in localUpdates:
                client_tools.download_file(constants.SERVER_ADDRESS, afile)
        if localDeletes:
            for afile in localDeletes:
                if os.path.isdir(afile):
                    os.rmdir(afile)
                else:
                    os.remove(afile)

    # Checks for new files every five minutes
    def run(self):
        while True:
            self.run_file_updates()
            time.sleep(self.interval * 60)  # sleeps for interval minutes


#Set your user path here (Could come from config file later)
#Creates a process to run in background and polls for file updates
def main():
    userhome = os.environ['HOME']
    pathname = userhome + '/Onedir'
    interval = 5
    checkMe = ServerChecker(pathname, interval)
    checkMe.run()

if __name__ == '__main__':
    main()

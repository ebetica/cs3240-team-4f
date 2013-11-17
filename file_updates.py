__author__ = 'robert'

import hashlib
import os
import pickle
import sys
import threading
import time
import client_tools
import constants
import server_tools
import csv


#Prototype to compare files on disk to those stored on a server
#Download listing of files on server -> create listing of files on local machine -> compare listings -> update necessary files
class ServerChecker(threading.Thread):
    path = ''  # path to OneDir directory
    interval = 5  # minutes between checking for updates


    def __init__(self, pathname, intervalIn):
        super(ServerChecker, self).__init__()
        userhome = os.environ['HOME']
        path = os.path.join(userhome, 'OneDir')
        if pathname:
            self.path = pathname
        else:
            self.path = path
        if not intervalIn is None:
            self.interval = intervalIn

    #Makes sure the Onedir directory exists on the local machine
    #If it doesn't, this creates the directory and returns false
    def check_directory(self):
        if not os.path.isdir(self.path):
            try:
                os.mkdir(self.path, 0700)
            except OSError:
                sys.exit( 'Cannot create OneDir directory')
            return False
        return True

    #Connects to server, downloads a listing of the user's files and then returns that listing
    def get_server_files(self):
        client_tools.download_file_updates(constants.SERVER_ADDRESS)
        fileListing = {}
        path = os.path.join(self.path, '.filelisting.onedir')  # Local machine path to dictionary of files from server

        if os.path.isfile(path):
            with open(path, 'r') as readerFile:
                reader = csv.reader(readerFile, delimiter=' ')
                for row in reader:
                    fileListing[row[0]] = row[1]
        return fileListing

    #Compares the file listings between server and local machine
    #Returns a list containing two lists
    #The first list is a list of files that need to be updated on the local machine
    #The second list is a list of files that need to be deleted from the local machine
    #TODO support directories
    def updateFiles(self, server):
        filesToDownload = []
        filesToUpload = []

        localfiles = os.listdir(self.path)
        for filename in server.keys():
            if not str.endswith(filename, '.delete'):
                if filename not in localfiles:
                    filesToDownload.append(filename)
                elif server[filename] > os.path.getmtime(os.path.join(self.path, filename)):
                    filesToDownload.append(filename)
                else:
                    filesToUpload.append(filename)
            else:
                filename = filename[:-7]
                os.remove(os.path.join(self.path, filename))

        localfiles = os.listdir(self.path)
        for filename in localfiles:
            if filename not in server.keys():
                filesToUpload.append(filename)
        return [filesToDownload, filesToUpload]

    #runner for file updates
    def run_file_updates(self):

        if self.check_directory():
            serverFiles = self.get_server_files()
            updateFiles = self.updateFiles(serverFiles)
            filesToDownload = updateFiles[0]
            filesToUpload = updateFiles[1]
        else:  # Directory doesn't exist, so no local files are on machine
            filesToDownload = self.get_server_files()  # Local machine needs all files from server
            filesToUpload = []  # No local files on machine means no updates need to be made to server
        if filesToDownload:
            for afile in filesToDownload:
                client_tools.download_file(constants.SERVER_ADDRESS, afile)
        if filesToUpload:
            for afile in filesToUpload:
                afile = os.path.join(self.path, afile)
                self.upload(afile)

    def upload(self, afile):
        if os.path.isdir(afile):
            for entry in os.listdir(afile):
                entry = os.path.join(afile, entry)
                if os.path.isdir(entry):
                    self.upload(entry)
                else:
                    client_tools.upload_file(constants.SERVER_ADDRESS, entry, os.path.getmtime(afile))
        else:
            client_tools.upload_file(constants.SERVER_ADDRESS, afile, os.path.getmtime(afile))

    # Checks for new files every five minutes
    def run(self):
        while True:
            self.run_file_updates()
            time.sleep(self.interval * 60)  # sleeps for interval minutes


#Set your user path here (Could come from config file later)
#Creates a process to run in background and polls for file updates
def main():
    userhome = os.environ['HOME']
    pathname = os.path.join(userhome, 'OneDir')
    interval = 5
    checkMe = ServerChecker(pathname, interval)
    checkMe.run()

if __name__ == '__main__':
    main()

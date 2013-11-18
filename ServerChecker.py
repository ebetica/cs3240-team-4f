__author__ = 'robert'
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
    interval = 5  # minutes between checking for updates


    def __init__(self, pathname, intervalIn):
        super(ServerChecker, self).__init__()
        userhome = os.environ['HOME']
        path = os.path.join(userhome, 'OneDir')
        if pathname:
            self.path = pathname
        else:
            self.path = path
        self.interval = intervalIn

    def check_updates(self):
        url = constants.SERVER_ADDRESS
        server_listing = client_tools.file_listing()
        server_files = {}
        local_listing = client_tools.get_file_paths()
        for afile in server_listing:
            afile = afile.split(' ')
            filename = afile[0]
            server_files[filename] = afile[1]
            if filename not in local_listing:
                client_tools.download_file(url, filename)
        for afile in local_listing:
            if afile not in server_files.keys():
                client_tools.upload_file(url, afile, os.path.getmtime(afile))
            elif server_files[afile] < os.path.getmtime(afile):
                client_tools.upload_file(url, afile, os.path.getmtime(afile))

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

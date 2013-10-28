__author__ = 'robert'

import pyinotify
import os
import client_tools
import constants

class MyEventHandler(pyinotify.ProcessEvent):

    def process_IN_CREATE(self, event):
        print "CREATE event:", event.pathname
        client_tools.upload_file(constants.SERVER_ADDRESS, event.pathname)

    def process_IN_DELETE(self, event):
        print "DELETE event:", event.pathname
        #Delete file from server. Probably going to write a new

    def process_IN_MODIFY(self, event):
        print "MODIFY event:", event.pathname
        client_tools.upload_file(constants.SERVER_ADDRESS, event.pathname)

class FileUpdateChecker():
    #TODO download updated files from server. Older file_updates.py code could be useful here

    def __init__(self, directory):
        self.path = directory
        self.watchManager = pyinotify.WatchManager()
        self.watchManager.add_watch(self.path, pyinotify.ALL_EVENTS, rec=True)
        self.eventHandler = MyEventHandler()
        self.notifier = pyinotify.ThreadedNotifier(self.watchManager, self.eventHandler)

    def start(self):
        self.notifier.start()

    def stop(self):
        self.notifier.stop()

def main():
    # watch manager
    ONEDIR_DIRECTORY = os.environ['HOME'] + '/OneDir'

    fu = FileUpdateChecker(ONEDIR_DIRECTORY)
    fu.start()
    fu.stop()

if __name__ == '__main__':
    main()

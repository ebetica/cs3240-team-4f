__author__ = 'robert'

import pyinotify
import os
import client_tools
import constants
from file_updates import ServerChecker


class MyEventHandler(pyinotify.ProcessEvent):
    uploadFiles = []

    def process_IN_CREATE(self, event):
        print "CREATE event:", event.pathname
        self.uploadFiles.append(event.pathname)
        if os.path.exists(event.pathname):
            r = client_tools.upload_file(constants.SERVER_ADDRESS, event.pathname, os.path.getmtime(event.pathname))
        if r == 200:
            self.uploadFiles.remove(event.pathname)

    def process_IN_DELETE(self, event):
        print "DELETE event:", event.pathname
        client_tools.delete_file(constants.SERVER_ADDRESS, event.pathname)

    def process_IN_MODIFY(self, event):
        print "MODIFY event:", event.pathname
        if os.path.exists(event.pathname):
            client_tools.upload_file(constants.SERVER_ADDRESS, event.pathname, os.path.getmtime(event.pathname))

class FileUpdateChecker():
    #TODO download updated files from server. Older file_updates.py code could be useful here

    def __init__(self, directory):
        self.path = directory
        self.watchManager = pyinotify.WatchManager()
        self.before = []
        if not os.path.isdir(self.path):
            os.mkdir(self.path, 0700)
        self.watchManager.add_watch(self.path, pyinotify.ALL_EVENTS, rec=True, auto_add=True)
        self.eventHandler = MyEventHandler()
        self.notifier = pyinotify.ThreadedNotifier(self.watchManager, self.eventHandler)
        self.interval = 1
        self.serverChecker = ServerChecker(self.path, self.interval)

    def start(self):
        '''
        if self.before:
            after = client_tools.get_file_paths(self.path)
            self.added = [f for f in after.keys() if not f in self.before.keys()]
            self.removed = [f for f in self.before.keys() if not f in after.keys()]
            self.modified = []
            for afile in self.before.keys():
                if afile in after.keys():
                    if after[afile] > self.before[afile]:
                        self.modified.append(afile)
        '''

        self.notifier.start()

    def stop(self):
        # Will never be called! Anything you put in here will be useless! HA!
        self.before = client_tools.get_file_paths(self.path)

        self.notifier.stop()


def main():
    # watch manager
    ONEDIR_DIRECTORY = os.path.join(os.environ['HOME'] + 'OneDir')

    fu = FileUpdateChecker(ONEDIR_DIRECTORY)
    fu.start()
    fu.stop()

if __name__ == '__main__':
    main()

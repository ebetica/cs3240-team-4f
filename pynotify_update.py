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
        if not os.path.isdir(self.path):
            os.mkdir(self.path, 0700)
        self.watchManager.add_watch(self.path, pyinotify.ALL_EVENTS, rec=True, auto_add=True)
        self.eventHandler = MyEventHandler()
        self.notifier = pyinotify.ThreadedNotifier(self.watchManager, self.eventHandler)
        self.interval = 1
        self.serverChecker = ServerChecker(self.path, self.interval)

    def start(self):
        self.notifier.start()

    def stop(self):

        self.notifier.stop()


def main():
    # watch manager
    ONEDIR_DIRECTORY = os.path.join(os.environ['HOME'] + 'OneDir')

    fu = FileUpdateChecker(ONEDIR_DIRECTORY)
    fu.start()


if __name__ == '__main__':
    main()

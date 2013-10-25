__author__ = 'robert'

import pyinotify
import os

class MyEventHandler(pyinotify.ProcessEvent):

    def process_IN_CREATE(self, event):
        print "CREATE event:", event.pathname
        #Upload the file to server

    def process_IN_DELETE(self, event):
        print "DELETE event:", event.pathname
        #Delete file from server

    def process_IN_MODIFY(self, event):
        print "MODIFY event:", event.pathname
        #Upload the file to the server

class FileUpdateChecker():

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
    ONEDIR_DIRECTORY = os.environ['HOME'] + '/Onedir'

    fu = FileUpdateChecker(ONEDIR_DIRECTORY)
    fu.start()
    fu.stop()

if __name__ == '__main__':
    main()

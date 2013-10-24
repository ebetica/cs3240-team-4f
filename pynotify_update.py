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

def main():
    # watch manager
    ONEDIR_DIRECTORY = os.environ['HOME'] + '/Onedir'

    wm = pyinotify.WatchManager()
    wm.add_watch(ONEDIR_DIRECTORY, pyinotify.ALL_EVENTS, rec=True)

    # event handler
    eh = MyEventHandler()

    # notifier
    notifier = pyinotify.ThreadedNotifier(wm, eh)
    notifier.start()

if __name__ == '__main__':
    main()

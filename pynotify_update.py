import client_tools
import constants
from file_updates import ServerChecker

import pyinotify
import os
import time


class MyEventHandler(pyinotify.ProcessEvent):
    uploadFiles = []

    def process_IN_CREATE(self, event):
        print "CREATE event:", event.pathname
        self.create_file(event.pathname)

    def process_IN_DELETE(self, event):
        print "DELETE event:", event.pathname
        client_tools.delete_file(constants.SERVER_ADDRESS, event.pathname)

    def process_IN_MODIFY(self, event):
        print "MODIFY event:", event.pathname
        if os.path.exists(event.pathname):
            client_tools.upload_file(constants.SERVER_ADDRESS, event.pathname, os.path.getmtime(event.pathname))

    def process_IN_MOVED_FROM(self, event):
        print "MOVE FROM event:", event.pathname
        self.process_IN_DELETE(event)

    def process_IN_MOVED_TO(self, event):
        print "MOVE TO event:", event.pathname
        self.process_IN_CREATE(event)

    def create_file(self, pathname):
        self.uploadFiles.append(pathname)
        if os.path.exists(pathname):
            r = client_tools.upload_file(constants.SERVER_ADDRESS, pathname, os.path.getmtime(pathname))
            if r == 200:
                self.uploadFiles.remove(pathname)
        

class FileUpdateChecker():

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

    def sync_with_server(self):
        while True:
            time.sleep(self.interval)
            username = client_tools.session()["username"]
            server_files = dict(client_tools.parse_listing(client_tools.file_listing()))
            client_files = dict(client_tools.parse_listing(username))

            # builds a listing of files on the local path
            local_files = {}
            for roots, dirs, files in os.walk(self.path):
                for f in files:
                    fp = os.path.join(roots, f)
                    mod_time = os.path.getmtime(fp)
                    local_files[fp] = mod_time


def main():
    # watch manager
    ONEDIR_DIRECTORY = os.path.join(os.environ['HOME'], 'OneDir')

    fu = FileUpdateChecker(ONEDIR_DIRECTORY)
    fu.start()


if __name__ == '__main__':
    main()

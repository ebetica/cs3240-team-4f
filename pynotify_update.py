import client_tools
import constants
from file_updates import ServerChecker

import pyinotify
import os
import time
from threading import Thread


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
        #self.serverChecker = ServerChecker(self.path, self.interval)

    def start(self):
        #Thread(target=self.sync_with_server).start()
        self.notifier.start()

    def stop(self):
        # We never get to this function because of how daemonizing works.
        pass

    def sync_with_server(self):
        while True:
            time.sleep(self.interval)
            username = client_tools.session()["username"]
            # Dictionary of file: (timestamp, deleted) for each file on the server.
            server_files = {k[0]:(k[1], k[2]) for k in 
                    client_tools.parse_listing(client_tools.file_listing())}
            prev_files = dict(client_tools.parse_listing(username))

            # builds a listing of files on the local path
            local_files = {}
            for roots, dirs, files in os.walk(self.path):
                for f in files:
                    fp = os.path.join(roots, f)
                    mod_time = os.path.getmtime(fp)
                    local_files[fp] = mod_time

            all_files = set(prev_files.keys()+local_files.keys())
            for f in all_files:
                state = (f in server_files, f in local_files)
                if state == (True, True):
                    if server_files[f][1] == "1":
                        # It's on both systems! Match timestamps and take the newest one :)
                        pass
                    elif server_files[f][1] == "0":
                        # It was once on the server but it has been deleted :(
                        #  Delete it from the client!
                        pass
                    pass
                if state == (True, False):
                    # It's in the server but not in the client!
                    if f in prev_files:
                        # It was in the client! The client must have deleted it :(
                        #  Delete it from the client.
                        pass
                    else:
                        # It wasn't in the client, so download it from the server.
                        pass
                    pass
                if state == (False, True):
                    # It's on the client but has never been on the server!
                    #  Upload it to the server!
                    pass
                if state == (False, False):
                    # It's not in either! hmm...
                    pass


def main():
    # watch manager
    ONEDIR_DIRECTORY = os.path.join(os.environ['HOME'], 'OneDir')

    fu = FileUpdateChecker(ONEDIR_DIRECTORY)
    fu.start()


if __name__ == '__main__':
    main()

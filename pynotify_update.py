import client_tools
import constants
from file_updates import ServerChecker

import pyinotify
import os, time, math
from threading import Thread


class MyEventHandler(pyinotify.ProcessEvent):
    uploadFiles = []

    def process_IN_CREATE(self, event):
        print "CREATE event:", event.pathname
        self.create_file(event.pathname)

    def process_IN_DELETE(self, event):
        print "DELETE event:", event.pathname
        client_tools.delete_file(event.pathname)

    def process_IN_MODIFY(self, event):
        print "MODIFY event:", event.pathname
        if os.path.exists(event.pathname):
            client_tools.upload_file(event.pathname, os.path.getmtime(event.pathname))

    def process_IN_MOVED_FROM(self, event):
        print "MOVE FROM event:", event.pathname
        self.process_IN_DELETE(event)

    def process_IN_MOVED_TO(self, event):
        print "MOVE TO event:", event.pathname
        self.process_IN_CREATE(event)

    def create_file(self, pathname):
        self.uploadFiles.append(pathname)
        if os.path.exists(pathname):
            r = client_tools.upload_file(pathname, os.path.getmtime(pathname))
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
        Thread(target=self.sync_with_server).start()
        self.notifier.start()

    def stop(self):
        # We never get to this function because of how daemonizing works.
        pass

    def sync_with_server(self):
        while True:
            time.sleep(self.interval)
            username = client_tools.session()["username"]
            OD = client_tools.read_config_file(username)
            # Dictionary of file: (timestamp, deleted) for each file on the server.
            server_files = {k[0]:(k[1], k[2]) for k in 
                    client_tools.parse_listing(client_tools.file_listing())}
            print(client_tools.parse_listing(username))
            prev_files = dict(client_tools.parse_listing(username, user = True))

            # builds a listing of files on the local path
            local_files = {}
            for roots, dirs, files in os.walk(self.path):
                for f in files:
                    fp = os.path.join(roots, f)
                    mod_time = os.path.getmtime(fp)
                    local_files[os.path.relpath(fp, OD)] = mod_time

            all_files = set(prev_files.keys()+local_files.keys())
            for f in all_files:
                # f is the relative file name, absf is the absolute filename
                absf = os.path.join(OD, f)
                state = (f in server_files, f in local_files)
                if state == (True, True):
                    if server_files[f][1] == "1":
                        server_time = math.trunc(float(server_files[f][0])*100) / 100.0
                        local_time  = math.trunc(local_files[f]*100) / 100.0
                        # It's on both systems! Match timestamps and take the newest one :)
                        print("It's on both systems! Match timestamps and take the newest one!")
                        print("File %s has timestamp %f on the server and %f timestamp on the client."%(f, server_time, local_time))
                        if server_time > local_time:
                            client_tools.download_file(f)
                        elif local_time > server_time:
                            client_tools.upload_file(absf, local_time)
                    elif server_files[f][1] == "0":
                        # It was once on the server but it has been deleted :(
                        #  Delete it from the client!
                        print("It was once on the server but it has been deleted :(")
                        client_tools.delete_file(absf)
                if state == (True, False):
                    # It's in the server but not in the client!
                    print("It's in the server but not in the client!")
                    if f in prev_files:
                        # It was in the client! The client must have deleted it :(
                        #  Delete it from the client listings.
                        client_tools.update_listings(username, f, 0, True)
                    else:
                        # It wasn't in the client, so download it from the server.  
                        client_tools.download_file(f)
                if state == (False, True):
                    # It's on the client but has never been on the server!
                    #  Upload it to the server!
                    print("It's on the client but has never been on the server!")
                    client_tools.upload_file(absf, os.path.getmtime(absf))
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

__author__ = 'robert'

from file_updates import FileChecker
import pickle
import os
import hashlib

#Safe way to hash large files (reads and hashes in chunks)
#From www.pythoncentral.io/hashing-files-with-python/
def safeHashFile( path):
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(path, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()

#Builds a dictionary of the local files on the machine
#Uses filename as key, and stores an md5 hash of each file as well as when the file was last modified
def get_local_files(fileOb):
    try:
        filelist = os.listdir(fileOb)
    except OSError:
        filelist = {}
    fileDict = {}
    for afile in filelist:
        if afile[0] is not '.':
            afile = (fileOb + '/' + afile)
            if os.path.isfile(afile):
                fileDict[afile] = [safeHashFile(afile), os.path.getmtime(afile)]
            elif os.path.exists(afile):
                fileDict.update(get_local_files(afile))
    return fileDict

def main():
    path = '/home/robert/ActualTestDir'
    pick = get_local_files(path)
    print pick
    pickle_path = path + '/.onedirdata.p'
    with open(pickle_path, 'wb') as pickle_file:
        pickle.dump(pick, pickle_file)


if __name__ == '__main__':
    main()
__author__ = 'robert'


import os
import unittest
from file_updates import FileChecker


class TestFileUpdates (unittest.TestCase):

    TEST_DIR = '/home/robert/TestDir'  # Change these for yourself
    EMPTY_DIR = '/home/robert/EmptyDir'
    test_dict = {'/home/robert/TestDir/file.file': ['0ca1a8d78c25cc35d60a8ce64c32b765', 1382281892.71026], '/home/robert/TestDir/constants.py': ['a25bde5a994ab01afd8bb83106e395cd', 1382281986.06226], '/home/robert/TestDir/downup.py': ['62127ece4ba0d6cfcb4d3c7aae04f2c8', 1382283352.30626], '/home/robert/TestDir/build_file_listing.py': ['372d1fa76d4949706fb2c82f83a3d404', 1382288982.1999247], '/home/robert/TestDir/constants.pyc': ['0dfe2c77655c3fbd1965381750187281', 1382281989.15026], '/home/robert/TestDir/banana.txt': ['ed076287532e86365e841e92bfc50d8c', 1382283357.20226], '/home/robert/TestDir/server.py': ['b953cbac298c5d7a97656d338da140ad', 1382281927.31026]}

    def test_InitNoArgs(self):
        fileChecker = FileChecker(None, None)
        userhome = os.environ['HOME']
        pathname = userhome + '/Onedir'
        self.assertEqual(fileChecker.interval, 5)
        self.assertEqual(fileChecker.path, pathname)

    def test_InitRootDir(self):
        interval = 5
        pathname = '/Onedir'
        fileChecker = FileChecker(pathname, interval)
        self.assertEqual(fileChecker.interval, interval)
        self.assertEqual(fileChecker.path, pathname)

    def test_CheckDirectoryRootDir(self):
        error_message = 'Cannot create onedir directory'
        interval = 5
        pathname = '/Onedir'
        fileChecker = FileChecker(pathname, interval)
        try:
            fileChecker.check_directory()
        except SystemExit, e:
            self.assertEqual(e.message, error_message)

    def test_CheckDirectoryHomeDir(self):
        fileChecker = FileChecker(None, None)
        if os.path.isdir(fileChecker.path):
            os.rmdir(fileChecker.path)
        fileChecker.check_directory()
        self.assertTrue(os.path.isdir(fileChecker.path))

    def test_GetServerFiles(self):
        fileChecker = FileChecker(self.TEST_DIR, 5)
        serverFiles = fileChecker.get_server_files()
        unmatched = set(serverFiles) ^ set(self.test_dict)
        self.assertTrue(len(unmatched) == 0)

    def test_GetEmptyServerFiles(self):
        fileChecker = FileChecker(self.EMPTY_DIR, 5)
        serverFiles = fileChecker.get_server_files()
        self.assertTrue(not serverFiles)

    def test_GetLocalFiles(self):
        fileChecker = FileChecker(self.TEST_DIR, 5)
        localFiles = fileChecker.get_local_files(self.TEST_DIR)
        unmatched = set(localFiles) ^ set(self.test_dict)
        self.assertTrue(len(unmatched) == 0)

    def test_GetEmptyLocalFiles(self):
        fileChecker = FileChecker(self.TEST_DIR, 5)
        localFiles = fileChecker.get_local_files(self.EMPTY_DIR)
        self.assertTrue(not localFiles)

    def test_NoUpdates(self):
        fileChecker = FileChecker(self.TEST_DIR, 5)
        localFiles = fileChecker.get_local_files(self.TEST_DIR)
        serverFiles = fileChecker.get_server_files()
        output = fileChecker.compareManifests(localFiles, serverFiles)
        for element in output:
            self.assertFalse(element)

    def test_AllUpdates(self):
        fileChecker = FileChecker(self.TEST_DIR, 5)
        localFiles = fileChecker.get_local_files(self.EMPTY_DIR)
        serverFiles = fileChecker.get_server_files()
        output = fileChecker.compareManifests(localFiles, serverFiles)
        self.assertEqual(output[0], self.test_dict.keys())
        self.assertFalse(output[1])
        self.assertFalse(output[2])
        self.assertFalse(output[3])


if __name__ == 'main':
    unittest.main()
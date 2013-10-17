__author__ = 'robert'


import os
import unittest
from file_updates import FileChecker


class TestFileUpdates (unittest.TestCase):
    def testInitNoArgs(self):
        fileChecker = FileChecker(None, None)
        userhome = os.environ['HOME']
        pathname = userhome + '/Onedir'
        self.assertEqual(fileChecker.interval, 5)
        self.assertEqual(fileChecker.path, pathname)


    def testInitRootDir(self):
        interval = 5
        pathname = '/Onedir'
        fileChecker = FileChecker(pathname, interval)
        self.assertEqual(fileChecker.interval, interval)
        self.assertEqual(fileChecker.path, pathname)

    def testCheckDirectoryRootDir(self):
        error_message = 'Cannot create onedir directory'
        interval = 5
        pathname = '/Onedir'
        fileChecker = FileChecker(pathname, interval)
        try:
            fileChecker.check_directory()
        except SystemExit, e:
            self.assertEqual(e.message, error_message)

    def testCheckDirectoryHomeDir(self):
        fileChecker = FileChecker(None, None)
        if os.path.isdir(fileChecker.path):
            os.rmdir(fileChecker.path)
        fileChecker.check_directory()
        self.assertTrue(os.path.isdir(fileChecker.path))

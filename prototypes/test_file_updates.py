__author__ = 'robert'


import unittest
from file_updates import FileChecker

class TestFileUpdates (unittest.TestCase):
    def testInitNoArgs(self):
        fileChecker = FileChecker()
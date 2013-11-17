
__author__ = 'robert'


import os
import unittest
from file_updates import ServerChecker


class TestFileUpdates (unittest.TestCase):
    def setUp(self):
        path = os.environ['HOME']
        path = os.path.join(path, 'OneDir')
        fileCheck = ServerChecker(path, 1)




if __name__ == '__main__':
    unittest.main()

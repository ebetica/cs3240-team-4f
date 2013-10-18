import os
import unittest
import tempfile
from constants import *

import server

class TestOneDir(unittest.TestCase):


    def setUp(self):
        self.db_fd, server.app.config['DATABASE'] = tempfile.mkstemp()
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        server.init_db()


    def test_empty_database(self):
        self.assertEqual(self.user_in_database("not_a_user"), FALSE)


    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(server.app.config['DATABASE'])


    def user_in_database(self, username):
        ret = self.app.post('/user_in_database', data=dict(
                    username=username), follow_redirects=True).data
        print(self.app.get.__doc__)
        return ret
        

if __name__ == '__main__':
    unittest.main()


import os
import unittest
import tempfile

import server

class TestOneDir(unittest.TestCase):


    def setUp(self):
        self.db_fd, server.app.config['DATABASE'] = tempfile.mkstemp()
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        server.init_db()


    def test_empty_database(self):
        self.assertEqual(self.user_in_database("not_a_user"), False)


    def test_register_login(self):
        name = "test_user"
        password = "password"
        self.assertEqual(self.register_user(name, password), True)
        self.assertEqual(self.login(name, password), True)
        self.assertEqual(self.login(name, "wrongpassword"), False)
        self.assertEqual(self.login("not-in-database", password), False)


    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(server.app.config['DATABASE'])


    def user_in_database(self, username):
        ret = self.app.get('/user_in_database', data=dict(
                    username=username), follow_redirects=True).data
        print(self.app.get.__doc__)
        return ret


    def register_user(self, username, password):
        ret = self.app.post('/register', data=dict(
                    username=username, password=password)
                    , follow_redirects=True).data
        return ret


    def login(self, username, password):
        ret = self.app.post('/register', data=dict(
                    username=username, password=password)
                    , follow_redirects=True).data
        return ret
        

if __name__ == '__main__':
    unittest.main()


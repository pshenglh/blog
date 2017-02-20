import os
import blog
import unittest
import tempfile

class blogTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, blog.app.config['DATABASE'] = tempfile.mkstemp()
        blog.app.config['TESTING'] = True
        self.app = blog.app.test_client()
        blog.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(blog.app.config['DATABASE'])

if __name__ == '__main__':
    unittest.main()
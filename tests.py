#  -*- coding: utf8 -*-
import os
import blog
import unittest
import tempfile
import sys

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)

    sys.setdefaultencoding(default_encoding)

class blogTestCase(unittest.TestCase):

    def setUp(self):
        blog.app.config['SQLALCHEMY_DATABASE_URI''] = tempfile.mkstemp()
        blog.app.config['TESTING'] = True
        self.app = blog.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        blog.db.create_all()
        self.client = user.app.test_client(user_cookies=True)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(blog.app.config['DATABASE'])

    def test_home_page(self):
        rv = self.app.get('/')
        self.assertTrue('文章' in rv.data)

if __name__ == '__main__':
    unittest.main()
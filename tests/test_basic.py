#  -*- coding: utf8 -*-
import unittest
from flask import current_app, url_for
from app import create_app, db
from app.models import Admin, Post, Comment


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_index(self):
        response = self.client.get(url_for('main.index'))
        self.assertTrue('文章' in response.data)

    def test_login_logout(self):
        admin = Admin(username='test',
                      password_hash='test1')
        db.session.add(admin)
        db.session.commit()
        user = Admin.query.filter_by(id=1).first()
        self.assertTrue('test'==user.username)
        self.assertTrue('test1'==user.password_hash)

        response = self.client.post(url_for('main.login'), data=dict(
            username='test',
            password='test1'
        ), follow_redirects=True)
        self.assertTrue('退出' in response.data)
        self.assertTrue('文章' in response.data)

        response = self.client.get(url_for('main.logout'), follow_redirects=True)
        self.assertTrue('登录' in response.data)
        self.assertTrue('文章' in response.data)

    def test_post(self):
        #添加用户并登录获取权限
        admin = Admin(username='test',
                      password_hash='test1')
        db.session.add(admin)
        db.session.commit()
        self.client.post(url_for('main.login'), data=dict(
            username='test',
            password='test1'
        ), follow_redirects=True)

        title_test = 'title_test'
        abstract_test = 'abstract_test'
        tag_test = 'code'
        body_test = 'body_test '

        #写博客
        response = self.client.post(url_for('main.write_post'), data=dict(
            title=title_test,
            abstract = abstract_test,
            tag=tag_test,
            body=body_test
        ), follow_redirects=True)
        self.assertTrue(response.status_code==200)
        p = Post.query.filter_by(title=title_test).first()
        self.assertTrue(p.abstract==abstract_test)
        self.assertTrue(p.tag==u'code-编程')
        self.assertTrue(p.body==body_test)

        #修改博客
        response = self.client.get(url_for('main.edit_post', id=p.id), follow_redirects=True)
        self.assertTrue(title_test in response.data)
        self.assertTrue(abstract_test in response.data)
        self.assertTrue('编程' in response.data)
        self.assertTrue(body_test in response.data)

        m_title_test = 'm_title_test'
        m_abstract_test = 'm_abstract_test'
        m_tag_test = 'net'
        m_body_test = 'm_body_test '
        response = self.client.post(url_for('main.edit_post', id=p.id), data=dict(
            title=m_title_test,
            abstract=m_abstract_test,
            tag=m_tag_test,
            body=m_body_test
        ), follow_redirects=True)
        self.assertTrue('文章' in response.data)
        p1 = Post.query.filter_by(id=p.id).first()
        self.assertTrue(p1.title==m_title_test)
        self.assertTrue(p1.abstract==m_abstract_test)
        self.assertTrue(p1.tag==u'net-网络')
        self.assertTrue(p1.body==m_body_test)

        # 查看博客
        # 评论功能
        comment = 'comment_test'
        connection = '123@456.com'
        self.client.post(url_for('main.post', id=p.id), data=dict(
            comment=comment,
            connect=connection
        ), follow_redirects=True)
        comments = Comment.query.filter_by(post_id=p.id).first()
        self.assertTrue(comments.connection == connection)
        self.assertTrue(comments.body == comment)
        response = self.client.get(url_for('main.post', id=p.id))
        self.assertTrue(response.status_code==200)
        self.assertTrue(p.title in response.data)
        self.assertTrue(comments.body in response.data)

        #删除评论
        self.client.post(url_for('main.delete_comment', id=comments.id))
        comment_del = Comment.query.filter_by(id=comments.id).first()
        self.assertIsNone(comment_del)

        #删除博客
        self.client.post(url_for('main.delete_post', id=p.id))
        p2 = Post.query.filter_by(id=p.id).first()
        self.assertIsNone(p2)

    def test_about_me(self):
        admin = Admin(username='test',
                      password_hash='test1',
                      about_me='about_me_test')
        db.session.add(admin)
        db.session.commit()
        self.client.post(url_for('main.login'), data=dict(
            username='test',
            password='test1'
        ), follow_redirects=True)

        response = self.client.get(url_for('main.about_me'), follow_redirects=True)
        self.assertTrue('about_me_test' in response.data)

        response = self.client.get(url_for('main.edit_about_me'), follow_redirects=True)
        self.assertTrue('about_me_test' in response.data)

        response = self.client.post(url_for('main.edit_about_me'), data=dict(
            about_me='m_about_me_test'
        ), follow_redirects=True)
        self.assertTrue('m_about_me_test' in response.data)





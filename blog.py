#  -*- coding: utf8 -*-
import sys
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flaskckeditor import CKEditor

# 处理中文编码的问题
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)

    sys.setdefaultencoding(default_encoding)

app = Flask(__name__)
db = SQLAlchemy(app)
manager = Manager(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SECRET_KEY'] = 'anxious'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

def make_shell_context():
    return dict(app=app, db=db, Admin=Admin, Post=Post,
                Comment=Comment)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm ()
    if form.validate_on_submit():
        user = Admin.query.filter_by(id=1).first()
        if user.username == form.email.data and \
                user.password_hash == form.password.data:
            admin = True
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.comment.data, post_id=id)
        db.session.add(comment)
        return redirect(url_for('post', id=id))
    post = Post.query.get_or_404(id)
    comments = Comment.query.filter_by(post_id=id).order_by(Comment.timestamp.desc()).all()
    return render_template('view_post.html', post=post, form=form, comments=comments)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    return redirect(url_for('index'))

@app.route('/delete_comment/<int:id>', methods=['GET', 'POST'])
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    post_id = comment.post_id
    db.session.delete(comment)
    return redirect(url_for('post', id=post_id))

@app.route('/', methods=['GET','POST'])
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('hello.html', posts=posts)

@app.route('/write_post', methods=['GET', 'Post'])
def write_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data)
        db.session.add(post)
        return redirect(url_for('index'))
    form.title.data = ''
    form.body.data = ''
    return render_template('post.html', form=form)

@app.route('/edit_post/<int:id>',methods=['GET','POST'])
def edit_post(id):
    form = PostForm()
    if form.validate_on_submit():
        post = Post.query.filter_by(id=id).first()
        post.body = form.body.data
        db.session.add(post)
        return redirect(url_for('index'))
    post = Post.query.filter_by(id=id).first()
    form.title.data = id
    form.body.data = post.body
    return render_template('post.html', form=form)

@app.route('/logout')
def logout():
    admin = False
    return redirect(url_for('index',))

class PostForm(Form,CKEditor):
    title = StringField('Enter Title',validators=[Required()])
    body = TextAreaField("What's on your mind?",validators=[Required()])
    submit = SubmitField('提交')

class LoginForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64)])
    password = PasswordField('密码', validators=[Required()])
    submit = SubmitField('登录')

class CommentForm(Form):
    connect = StringField('联系方式')
    comment = TextAreaField('评论', validators=[Required()])
    submit = SubmitField('提交')

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='role')

    def __repr__(self):
        return '<User %r>' % self.username

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

if __name__ == '__main__':
    manager.run()
    app.run(debug=True)
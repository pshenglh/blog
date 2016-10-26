#  -*- coding: utf8 -*-
import sys
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flaskckeditor import CKEditor
from flask_login import LoginManager, login_user, UserMixin, login_required, logout_user
from flask_moment import Moment
import time

# 处理中文编码的问题
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)

    sys.setdefaultencoding(default_encoding)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'

app = Flask(__name__)
db = SQLAlchemy(app)
manager = Manager(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db)
basedir = os.path.abspath(os.path.dirname(__file__))
login_manager.init_app(app)
moment = Moment(app)


app.config['SECRET_KEY'] = 'anxious'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

def make_shell_context():
    return dict(app=app, db=db, Admin=Admin, Post=Post,
                Comment=Comment)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm ()
    if form.validate_on_submit():
        user = Admin.query.filter_by(id=1).first()
        if user.username == form.email.data and \
                user.password_hash == form.password.data:
            login_user(user, False)
        return redirect(request.args.get('next') or url_for('index'))
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
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    return redirect(url_for('index'))

@app.route('/delete_comment/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    post_id = comment.post_id
    db.session.delete(comment)
    return redirect(url_for('post', id=post_id))

@app.route('/', methods=['GET','POST'])
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    if len(posts) < 10:
        new_posts = posts
    else:
        new_posts = posts[0:9]
    return render_template('hello.html', posts=posts, new_posts=new_posts)

@app.route('/code')
def code():
    posts = Post.query.filter_by(tag='code').order_by(Post.timestamp.desc()).all()
    return render_template('hello.html', posts=posts)

@app.route('/database')
def database():
    posts = Post.query.filter_by(tag='database').order_by(Post.timestamp.desc()).all()
    return render_template('hello.html', posts=posts)

@app.route('/essay')
def essay():
    posts = Post.query.filter_by(tag='essay').order_by(Post.timestamp.desc()).all()
    return render_template('hello.html', posts=posts)

@app.route('/write_post', methods=['GET', 'POST'])
@login_required
def write_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, title=form.title.data, abstract=form.abstract.data,
                    tag=form.tag.data)
        print post.timestamp
        db.session.add(post)
        return redirect(url_for('index'))
    form.title.data = ' '
    form.abstract.data = ' '
    form.tag.data = 'code'
    form.body.data = ' '
    return render_template('post.html', form=form)

@app.route('/edit_post/<int:id>',methods=['GET','POST'])
@login_required
def edit_post(id):
    form = PostForm()
    if form.validate_on_submit():
        print 1
        post = Post.query.filter_by(id=id).first()
        post.body = form.body.data
        post.title = form.title.data
        post.abstract = form.abstract.data
        post.tag = form.tag.data
        db.session.add(post)
        return redirect(url_for('index'))
    post = Post.query.filter_by(id=id).first()
    form.title.data = post.title
    form.tag.data = post.tag
    form.body.data = post.body
    form.abstract.data = post.abstract
    print post.timestamp
    return render_template('post.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index',))

class PostForm(Form,CKEditor):
    title = StringField('标题',validators=[Required()])
    abstract = TextAreaField('摘要',validators=[Required()])
    tag = SelectField('标签', choices=[('code', '编程'), ('database', '数据库'),('essay', '随笔')], validators=[Required()])
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

class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    abstract = db.Column(db.Text)
    tag = db.Column(db.Text)
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
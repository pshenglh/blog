#  -*- coding: utf8 -*-
import sys
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import  Bootstrap
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from flask_script import Manager, Shell

#处理中文编码的问题
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)

    sys.setdefaultencoding(default_encoding)

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SECRET_KEY'] = 'anxious'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)

def make_shell_context():
    return dict(app=app, db=db, Admin=Admin, Post=Post, \
                Comment=Comment)
manager.add_command("shell", Shell(make_context=make_shell_context))

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('hello.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(id=1).first()
        if user.username == form.email.data and \
                user.password_hash == form.password.data:
            admin = True
        return render_template('hello.html', admin=admin)
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    admin = False
    return redirect(url_for('index'))

class LoginForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64)])
    password = PasswordField('密码', validators=[Required()])
    submit = SubmitField('登录')

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
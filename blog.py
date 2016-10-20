#  -*- coding: utf8 -*-
import sys
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import  Bootstrap
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Required, Length

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)

    sys.setdefaultencoding(default_encoding)

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'anxious'

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('hello.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.email.data
        password = form.password.data
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

class LoginForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64)])
    password = PasswordField('密码', validators=[Required()])
    submit = SubmitField('登录')

if __name__ == '__main__':
    app.run(debug=True)
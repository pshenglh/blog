#  -*- coding: utf8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import Required, Length
from flaskckeditor import CKEditor

import sys

# 处理中文编码的问题
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)

    sys.setdefaultencoding(default_encoding)


class PostForm(FlaskForm,CKEditor):
    title = StringField('标题',validators=[Required()])
    abstract = TextAreaField('摘要',validators=[Required()])
    tag = SelectField('标签', choices=[('code', '编程'), ('database', '数据库'),('essay', '随笔'), \
                                     ('tools', '工具'), ('net', '网络')], validators=[Required()])
    body = TextAreaField("What's on your mind?",validators=[Required()])
    submit = SubmitField('提交')

class AbooutMeForm(FlaskForm, CKEditor):
    about_me = TextAreaField('关于我', validators=[Required()])
    submit = SubmitField('提交')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[Required(), Length(1, 64)])
    password = PasswordField('密码', validators=[Required()])
    submit = SubmitField('登录')

class CommentForm(FlaskForm):
    connect = StringField('联系方式')
    comment = TextAreaField('评论', validators=[Required()])
    submit = SubmitField('提交')

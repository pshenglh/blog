#  -*- coding: utf8 -*-
import sys
from flask import Flask, render_template, redirect, url_for, request, flash
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
from werkzeug import secure_filename

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

UPLOAD_FOLDER = 'static/pic'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['SECRET_KEY'] = 'anxious'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024



def make_shell_context():
    return dict(app=app, db=db, Admin=Admin, Post=Post,
                Comment=Comment)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# 登录
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

# 登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index',))

# 修改评论
@app.route('/delete_comment/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    post_id = comment.post_id
    db.session.delete(comment)
    return redirect(url_for('post', id=post_id))

def find_new_post():
    page = request.args.get('page', 1, type=int)
    new_post = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=20, error_out=False
    )
    new_posts = new_post.items
    return new_posts

# 文章首页和分类
@app.route('/', methods=['GET','POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=5, error_out=False)
    posts = pagination.items
    new_posts = find_new_post()
    return render_template('index.html', posts=posts, new_posts=new_posts,
                           pagination=pagination)

# 关于我
@app.route('/about_me')
def about_me():
    user = Admin.query.filter_by(id=1).first()
    return render_template('about_me.html', user=user)

@app.route('/edit_abtme', methods=['GET', 'POST'])
def edit_about_me():
    form = AbooutMeForm()
    user = Admin.query.filter_by(id=1).first()
    if request.method == 'POST':
        user.about_me = form.about_me.data
        db.session.add(user)
        return redirect(url_for('index'))
    form.about_me.data = user.about_me
    return render_template('edit_about_me.html', form=form)


@app.route('/code')
def code():
    posts = Post.query.filter_by(tag='code').order_by(Post.timestamp.desc()).all()
    new_posts = find_new_post()
    return render_template('index.html', posts=posts, new_posts=new_posts)

@app.route('/database')
def database():
    posts = Post.query.filter_by(tag='database').order_by(Post.timestamp.desc()).all()
    new_posts = find_new_post()
    return render_template('index.html', posts=posts, new_posts=new_posts)

@app.route('/essay')
def essay():
    posts = Post.query.filter_by(tag='essay').order_by(Post.timestamp.desc()).all()
    new_posts = find_new_post()
    return render_template('index.html', posts=posts, new_posts=new_posts)

@app.route('/tool')
def tool():
    posts = Post.query.filter_by(tag='tools').order_by(Post.timestamp.desc()).all()
    new_posts = find_new_post()
    return render_template('index.html', posts=posts, new_posts=new_posts)

@app.route('/net')
def net():
    posts = Post.query.filter_by(tag='net').order_by(Post.timestamp.desc()).all()
    new_posts = find_new_post()
    return render_template('index.html', posts=posts, new_posts=new_posts)

# 编写博客
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
    return render_template('write_post.html', form=form, id=0)

# 修改博客
@app.route('/edit_post/<int:id>',methods=['GET','POST'])
@login_required
def edit_post(id):
    form = PostForm()
    if form.validate_on_submit():
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
    if post.body_pic:
        p = post.body_pic.split("|")
    else:
        p = None
    return render_template('post.html', form=form, id=id, filenam=p)

# 删除博客
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    comments = Comment.query.filter_by(post_id=id).all()
    if comments:
        db.session.delete(comments)
    if post.head_pic:
        q = post.head_pic[1:]
        if os.path.exists(q):
            os.remove(q)
    if post.body_pic:
        p = post.body_pic.split("|")
        for i in p:
            l = i[1:]
            if os.path.exists(l):
                os.remove(l)
        r = os.path.split(p[0])
        if os.path.exists(r[0][1:]):
            os.rmdir(r[0][1:])
    return redirect(url_for('index'))

# 查看博客
@app.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.comment.data, connection=form.connect.data, post_id=id)
        db.session.add(comment)
        return redirect(url_for('post', id=id))
    post = Post.query.get_or_404(id)
    comments = Comment.query.filter_by(post_id=id).order_by(Comment.timestamp.desc()).all()
    return render_template('view_post.html', post=post, form=form, comments=comments)

# 文件上传
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploaded_file/<id>', methods=['GET', 'POST'])
@login_required
def uploaded_file(id):
    post = Post.query.filter_by(id=id).first()
    p =post.head_pic
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            pic_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            s = os.path.split(pic_path)
            p = '/' + s[0] + '/' + s[1]
            post = Post.query.filter_by(id=id).first()
            if post.head_pic:
                q = os.path.split(post.head_pic)
                l = s[0] + '/' + q[1]
                if os.path.exists(l):
                    os.remove(l)
            post.head_pic = p
    return render_template('theme_pic.html', filenam=p, id=id)

@app.route('/post_pic/<int:id>',methods=['GET','POST'])
@login_required
def post_pic(id):
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            post = Post.query.filter_by(id=id).first()
            filename = secure_filename(file.filename)
            if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], '0'+str(post.id))):
                os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], '0'+str(post.id)))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], '0'+str(post.id), filename))
            pic_path = os.path.join(app.config['UPLOAD_FOLDER'], '0'+str(post.id), filename)
            s = os.path.split(pic_path)
            p = '/' + s[0] + '/' + s[1]
            if not post.body_pic:
                post.body_pic = p
            else:
                post.body_pic = post.body_pic + '|' + p
            return redirect(url_for( id=id))
    return render_template('upload_file.html')

@app.route('/uploaded-postpic/<id>')
@login_required
def uploaded_postpic(id):
    post = Post.query.filter_by(id=id).first()
    if post.body_pic:
        p = post.body_pic.split("|")
    else:
        p = None
    return render_template('body_pic.html', filenam=p, id=id)

# 错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

class PostForm(Form,CKEditor):
    title = StringField('标题',validators=[Required()])
    abstract = TextAreaField('摘要',validators=[Required()])
    tag = SelectField('标签', choices=[('code', '编程'), ('database', '数据库'),('essay', '随笔'), \
                                     ('tools', '工具'), ('net', '网络')], validators=[Required()])
    body = TextAreaField("What's on your mind?",validators=[Required()])
    submit = SubmitField('提交')

class AbooutMeForm(Form, CKEditor):
    about_me = TextAreaField('关于我', validators=[Required()])
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
    user_pic = db.Column(db.Text)
    about_me = db.Column(db.Text)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    head_pic = db.Column(db.Text, default='/static/pic/test3.jpg')
    body_pic = db.Column(db.Text)
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
    connection = db.Column(db.Text)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

if __name__ == '__main__':
    manager.run()
    app.run(debug=True)
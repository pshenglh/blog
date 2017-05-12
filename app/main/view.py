#  -*- coding: utf-8 -*-
import sys
from flask import render_template, redirect, url_for, request, current_app, make_response
import os
from flask_login import login_user, login_required, logout_user
from werkzeug import secure_filename
from ..models import Admin, Post, Comment
from .Forms import PostForm, AbooutMeForm, CommentForm, LoginForm
from .. import db, login_manager
from . import main
from wtforms.compat import iteritems

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# 登录
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm ()
    #for name, fields in iteritems(form._fields):
     #   print name, fields.validate(form)
    #print form.validate()
    #print form.username.validate(form), form.password.validate(form), form.submit.validate(form)
    #print form.csrf_token.validate(form), form.validate()
    if request.method == 'POST':
        user = Admin.query.filter_by(id=1).first()
        if user.username == form.username.data and \
                user.password_hash == form.password.data:
            login_user(user, False)
        return redirect(url_for('main.index'))
    return render_template('login.html', form=form)

# 登出
@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# 修改评论
@main.route('/delete_comment/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    post_id = comment.post_id
    db.session.delete(comment)
    return redirect(url_for('main.post', id=post_id))

def find_new_post():
    page = request.args.get('page', 1, type=int)
    new_post = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=20, error_out=False
    )
    new_posts = new_post.items
    return new_posts

# 文章首页和分类
@main.route('/', methods=['GET','POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=5, error_out=False)
    posts = pagination.items
    new_posts = find_new_post()
    return render_template('index.html', posts=posts, new_posts=new_posts,
                           pagination=pagination)

# 关于我
@main.route('/about_me')
def about_me():
    user = Admin.query.filter_by(id=1).first()
    return render_template('about_me.html', user=user)

@main.route('/edit_abtme', methods=['GET', 'POST'])
@login_required
def edit_about_me():
    form = AbooutMeForm()
    user = Admin.query.filter_by(id=1).first()
    if request.method == 'POST':
        user.about_me = form.about_me.data
        db.session.add(user)
        return redirect(url_for('main.about_me'))
    form.about_me.data = user.about_me
    return render_template('edit_about_me.html', form=form)


@main.route('/code')
def code():
    posts = Post.query.filter_by(tag='code').order_by(Post.timestamp.desc()).all()
    new_posts = find_new_post()
    return render_template('index.html', posts=posts, new_posts=new_posts)

@main.route('/database')
def database():
    posts = Post.query.filter_by(tag='database').order_by(Post.timestamp.desc()).all()
    new_posts = find_new_post()
    return render_template('index.html', posts=posts, new_posts=new_posts)

@main.route('/essay')
def essay():
    posts = Post.query.filter_by(tag='essay').order_by(Post.timestamp.desc()).all()
    new_posts = find_new_post()
    return render_template('index.html', posts=posts, new_posts=new_posts)

@main.route('/tool')
def tool():
    posts = Post.query.filter_by(tag='tools').order_by(Post.timestamp.desc()).all()
    new_posts = find_new_post()
    return render_template('index.html', posts=posts, new_posts=new_posts)

@main.route('/net')
def net():
    posts = Post.query.filter_by(tag='net').order_by(Post.timestamp.desc()).all()
    new_posts = find_new_post()
    return render_template('index.html', posts=posts, new_posts=new_posts)

def tag_get(form):
    for value, label in form.tag.choices:
        if value == form.tag.data:
            u_label = unicode(label, 'utf-8')
            t = (value, u_label)
            tag = '-'.join(t)
            return tag

@main.app_template_filter('tag_get')
def tag(s):
    list = str(s).split('-')
    return list[1]


@main.route('/mod')
def form_tag_modify():
    posts = Post.query.all()
    for p in posts:
        form = PostForm()
        form.tag.data = p.tag
        tag = tag_get(form)
        print tag
        p.tag = tag
        db.session.add(p)
    return make_response('success')

# 编写博客
@main.route('/write_post', methods=['GET', 'POST'])
@login_required
def write_post():
    form = PostForm()
    if request.method == 'POST':
        post = Post(body=form.body.data, title=form.title.data, abstract=form.abstract.data,
                    tag=tag_get(form))
        print tag_get(form)
        db.session.add(post)
        return redirect(url_for('main.index'))
    form.title.data = ' '
    form.abstract.data = ' '
    form.tag.data = 'code'
    form.body.data = ' '
    return render_template('write_post.html', form=form, id=0)

# 修改博客
@main.route('/edit_post/<int:id>',methods=['GET','POST'])
@login_required
def edit_post(id):
    form = PostForm()
    if request.method == 'POST':
        post = Post.query.filter_by(id=id).first()
        post.body = form.body.data
        post.title = form.title.data
        post.abstract = form.abstract.data
        post.tag = tag_get(form)
        db.session.add(post)
        return redirect(url_for('main.index'))
    post = Post.query.filter_by(id=id).first()
    form.title.data = post.title
    form.tag.data = str(post.tag).split('-')[0]
    form.body.data = post.body
    form.abstract.data = post.abstract
    if post.body_pic:
        p = post.body_pic.split("|")
    else:
        p = None
    return render_template('post.html', form=form, id=id, filenam=p)

# 删除博客
@main.route('/delete/<int:id>', methods=['GET', 'POST'])
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
    return redirect(url_for('main.index'))

# 查看博客
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    form = CommentForm()
    if request.method == 'POST':
        comment = Comment(body=form.comment.data, connection=form.connect.data, post_id=id)
        db.session.add(comment)
        return redirect(url_for('main.post', id=id))
    post = Post.query.get_or_404(id)
    comments = Comment.query.filter_by(post_id=id).order_by(Comment.timestamp.desc()).all()
    return render_template('view_post.html', post=post, form=form, comments=comments)

# 文件上传
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']

@main.route('/uploaded_file/<id>', methods=['GET', 'POST'])
@login_required
def uploaded_file(id):
    post = Post.query.filter_by(id=id).first()
    p = post.head_pic
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(current_app.config['BASE_DIR'],
                                current_app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            p = os.path.join(current_app.config['PIC_FOLDER'], filename)
            post = Post.query.filter_by(id=id).first()
            if post.head_pic:
                q = post.head_pic
                if os.path.exists(q):
                    os.remove(q)
            post.head_pic = p
    return render_template('theme_pic.html', filenam=p, id=id)

@main.route('/post_pic/<int:id>',methods=['GET','POST'])
@login_required
def post_pic(id):
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            post = Post.query.filter_by(id=id).first()
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.config['BASE_DIR'], current_app.config['UPLOAD_FOLDER'],
                                         '0'+str(post.id))
            if not os.path.exists(upload_folder):
                os.mkdir(upload_folder)
            file.save(os.path.join(upload_folder, filename))
            pic_path = os.path.join(current_app.config['PIC_FOLDER'], '0'+str(post.id), filename)
            if not post.body_pic:
                post.body_pic = pic_path
            else:
                post.body_pic = post.body_pic + '|' + p
            return redirect(url_for('main.edit_post', id=id))
    return render_template('upload_file.html')

@main.route('/uploaded-postpic/<id>')
@login_required
def uploaded_postpic(id):
    post = Post.query.filter_by(id=id).first()
    if post.body_pic:
        p = post.body_pic.split("|")
    else:
        p = None
    return render_template('body_pic.html', filenam=p, id=id)

# 错误处理
@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
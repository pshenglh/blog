import os

basedir = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = basedir
UPLOAD_FOLDER = 'app/static/pic'
PIC_FOLDER = '/static/pic'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

SECRET_KEY = 'anxious'
SQLALCHEMY_DATABASE_URI = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
UPLOAD_FOLDER = UPLOAD_FOLDER
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
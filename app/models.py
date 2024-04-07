from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import UserMixin
from app import login

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=False)
    description = db.Column(db.Text, unique=False)
    filename = db.Column(db.String(64), unique=False)
    file_path = db.Column(db.String(64), unique=False)
    thumbnail = db.Column(db.String(64), unique=False)
    thumbnail_path = db.Column(db.String(64), unique=False)
    author = db.Column(db.String(64), unique=False)

    def __repr__(self):
        return '<Filename {}>'.format(self.filename)

    def secure_filename(self):
        self.filename = secure_filename(self.filename)

    def secure_thumbnail(self):
        self.thumbnail = secure_filename(self.thumbnail)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.Integer)
    author = db.Column(db.String(64))
    text = db.Column(db.Text)

    def __repr__(self):
        return '<Comment {}.{}>'.format(self.upload_id, self.id)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
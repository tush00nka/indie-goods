from app import app
from flask import render_template, flash, redirect, url_for, send_from_directory, request, send_file
from app.forms import LoginForm, RegisterForm, UploadForm, UploadPageCommentForm, SearchForm
import os
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Upload, Comment
from app import db
from io import BytesIO
import time

basedir = os.path.abspath(os.path.dirname(__file__))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'logo.png')

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
    uploads = []
    thumbnail_path = str(os.path.join(basedir, 'thumbnails'))

    form = SearchForm()
    if form.validate_on_submit():
        for upload in Upload.query.all():
            if str(form.query.data).lower() in (str(upload.title) + str(upload.description) + str(upload.author)).lower():
                uploads.append(upload)
    else:
        uploads = Upload.query.all()
    uploads.reverse()
    return render_template('index.html', form=form, uploads=uploads, thumbnail_path=thumbnail_path)


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверный логин или пароль', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page:
            next_page = url_for('index')
        flash('Успешный вход', "success")
        return redirect(next_page)

    return render_template('login.html', form=form, title="Вход")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('Имя пользователя занято', 'danger')
            return redirect(url_for('register'))

        if form.password.data != form.password_confirm.data:
            flash('Пароли не совпадают', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        next_page = request.args.get('next')
        if not next_page:
            next_page = url_for('index')

        flash('Успешная регистрация', "success")
        return redirect(next_page)

    return render_template('register.html', form=form, title="Регистрация")
    

@app.route('/lk', methods=['GET','POST'])
@login_required
def lk():
    uploads = Upload.query.all()
    uploads.reverse()
    thumbnail_path = str(os.path.join(basedir, 'thumbnails'))
    return render_template('lk.html', title="Личный кабинет", uploads=uploads, thumbnail_path=thumbnail_path)


@app.route('/logout')
def logout():
    logout_user()
    flash('Вы вышли из системы', 'warning')
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET','POST'])
def upload():
    if current_user.is_authenticated:
        form = UploadForm()

        if form.validate_on_submit():
            time_since_epoch = str(int(time.time()))
            new_upload = Upload(title=form.title.data, description=form.description.data, filename=time_since_epoch + form.file.data.filename, author=current_user.username, thumbnail= time_since_epoch + form.image.data.filename)
            new_upload.secure_filename()
            new_upload.secure_thumbnail()

            file_path = os.path.join(basedir, 'static/uploads/') + new_upload.filename
            thumbnail_path = os.path.join(basedir, 'static/thumbnails/') + new_upload.thumbnail

            form.file.data.save(file_path)
            form.image.data.save(thumbnail_path)

            new_upload.file_path = file_path
            new_upload.thumbnail_path = thumbnail_path

            db.session.add(new_upload)
            db.session.commit()

            next_page = request.args.get('next')
            if not next_page:
                next_page = url_for('index')

            flash('Успешная публикация', "success")
            return redirect(next_page)

        return render_template('upload.html', form=form, title="Публикация")

    return redirect(url_for('index'))


@app.route('/download/<upload_id>')
def download(upload_id):
    upload = Upload.query.filter_by(id=upload_id).first()
    return send_file(upload.file_path, download_name=upload.filename, as_attachment=True)


@app.route('/uploads/<upload_id>', methods=['GET','POST'])
def upload_page(upload_id):
    upload = Upload.query.filter_by(id=upload_id).first()
    form = UploadPageCommentForm()

    if current_user.is_authenticated:
        if form.validate_on_submit():
            new_comment = Comment(upload_id=upload.id, author=current_user.username, text=form.comment.data)

            db.session.add(new_comment)
            db.session.commit()

            next_page = request.args.get('next')
            if not next_page:
                next_page = url_for('upload_page', upload_id=upload_id)

            flash('Вы оставили комментарий', "success")
            return redirect(next_page)

    comments = Comment.query.all()

    return render_template('upload_page.html', upload=upload, form=form, comments=comments)

@app.route('/uploads/<upload_id>/delete/<comment_id>')
def delete_comment(upload_id, comment_id):
    if current_user.is_authenticated:
        comment = Comment.query.filter_by(id=comment_id).first()
        if current_user.username == comment.author:
            Comment.query.filter_by(id=comment_id).delete()
            db.session.commit()
            flash('Комментарий удалён', "danger")
    
    return redirect(url_for('upload_page', upload_id=upload_id))
            

@app.route('/delete/<upload_id>')
def delete(upload_id):

    if current_user.is_authenticated:

        upload = Upload.query.filter_by(id=upload_id).first()
        if current_user.username == upload.author:
            os.remove(os.path.join(basedir, f'static/uploads/{upload.filename}'))
            os.remove(os.path.join(basedir, f'static/thumbnails/{upload.thumbnail}'))
            Upload.query.filter_by(id=upload_id).delete()
            db.session.commit()
        return redirect(url_for('lk'))
    
    return redirect(url_for('index'))

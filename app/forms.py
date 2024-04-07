from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_confirm = PasswordField('Подтвердите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class UploadForm(FlaskForm):
    title = StringField('Название публикации', validators=[DataRequired()])
    description = TextAreaField('Описание')
    image = FileField('Обложка публикации (256x256)', validators=[DataRequired()])
    file = FileField('Файл', validators=[DataRequired()])
    submit = SubmitField('Загрузить')


class UploadPageCommentForm(FlaskForm):
    comment = TextAreaField('Комментарий...', validators=[DataRequired()])
    submit = SubmitField('Оставить комментарий')

class SearchForm(FlaskForm):
    query = StringField('Поиск')
    submit = SubmitField('Поиск')
"""
Формы приложения.
"""

import urllib3
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField, validators
from wtforms.validators import InputRequired, URL, ValidationError
from app.models import Content
from app import db_lib

from app.models import User


class LoginForm(FlaskForm):
    """
    Форма авторизации.
    """
    nickname = StringField('Никнейм', validators=[InputRequired()])
    password = PasswordField('Пароль', validators=[InputRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

    def validate_nickname(self, nickname):
        user = User.query.filter_by(nickname=nickname.data).first()
        if user and not user.active:
            raise ValidationError('Учётная запись неактивна.')

    class Meta:
        csrf = True


class RegForm(FlaskForm):
    """
    Форма регистрации пользователя.
    """
    nickname = StringField(
        'Никнейм',
        validators=[InputRequired(message='Заполните поле!')]
    )
    password1 = PasswordField('Пароль', [
        validators.InputRequired(message='Заполните поле!'),
        validators.EqualTo('password2', message='Пароли должны совпадать!')
    ])
    password2 = PasswordField('Пароль повторно', [
        validators.InputRequired(message='Заполните поле!')
    ])

    def validate_nickname(self, nickname):
        user = User.query.filter_by(nickname=nickname.data).first()
        if user is not None:
            raise ValidationError('Ник занят. Выберите другой, пожалуйста.')

    class Meta:
        csrf = True


class NewDataForm(FlaskForm):
    """
    Форма добавления новой записи в базу данных.
    """
    name = StringField('Название (описание)',
                       validators=[InputRequired(message='Поле должно содержать текст и не может быть пустым')])
    url = StringField('Ссылка', validators=[
        URL(require_tld=False, message='Неверно указан URL'),
        InputRequired(message='Поле обязательно для заполнения')
    ])
    lang = SelectField('Язык')
    category = SelectField('Категория')
    types = SelectField('Тип')

    def validate_url(self, urls):
        exists = db_lib.session.query(db_lib.exists().where(Content.url == urls.data)).scalar()
        if exists:
            raise ValueError('Ссылка на этот ресурс уже есть в нашей базе.')

        try:
            http = urllib3.PoolManager()
            response = http.request('GET', urls.data)
        except:
            raise ValidationError('Ссылка недоступна или работает неправильно.')
        else:
            if response.status not in (200, 301, 302):
                raise ValidationError('Проверьте, что ссылка работает и ведёт на открытый ресурс.')

    def validate_lang(self, choice):
        pass

    def validate_category(self, choice):
        pass

    def validate_types(self, choice):
        pass

    class Meta:
        csrf = True

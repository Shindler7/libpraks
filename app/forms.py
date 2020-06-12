"""
Формы приложения.
"""

import urllib3
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import BooleanField, PasswordField, SelectField
from wtforms import StringField, SubmitField, validators
from wtforms.validators import InputRequired, URL, ValidationError

from app import db_lib
from app.models import Category, Content, Types
from app.models import User


class LoginForm(FlaskForm):
    """
    Форма авторизации.
    """
    nickname = StringField(
        'Никнейм',
        validators=[InputRequired(message='Заполните поле!')]
    )
    password = PasswordField('Пароль', validators=[InputRequired()])
    remember_me = BooleanField('Запомнить меня')
    recaptcha = RecaptchaField()
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
    recaptcha = RecaptchaField()

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
                       validators=[InputRequired(
                           message='Поле должно содержать текст'
                                   ' и не может быть пустым')])
    url = StringField('Ссылка', validators=[
        URL(require_tld=False, message='Неверно указан URL'),
        InputRequired(message='Поле обязательно для заполнения')
    ])

    lang = SelectField('Язык',
                       choices=[])
    category = SelectField('Категория',
                           choices=[],
                           coerce=int)
    types = SelectField('Тип',
                        choices=[],
                        coerce=int)

    def validate_url(self, urls):

        exists = db_lib.session.query(db_lib.exists().where(
            Content.url == urls.data)).scalar()
        if exists:
            raise ValueError('Ссылка на этот ресурс уже есть в нашей базе.')

        try:
            http = urllib3.PoolManager()
            response = http.request('GET', urls.data)
        except Exception:
            raise ValidationError('Ссылка недоступна или '
                                  'работает неправильно.')
        else:
            if response.status != 200:
                raise ValidationError('Проверьте, что ссылка работает '
                                      'и ведёт на открытый ресурс.')

    class Meta:
        csrf = True


class CategoryForm(FlaskForm):

    name = StringField('Имя',
                       validators=[InputRequired(
                           message='Поле должно содержать текст')])
    fname = StringField('Slug')

    def validate_name(self, name):

        field = name.data.strip().lower()
        if not field:
            self.name.errors.append('Поле необходимо заполнить.')
            return False

        exists = db_lib.session.query(db_lib.exists().where(
            Category.name == field)).scalar()
        if exists:
            self.name.errors.append('Это название уже используется.')
            return False

        return True

    def validate_fname(self, fname):

        if fname.data is None:
            return True

        field = fname.data.strip().lower()

        exists = db_lib.session.query(db_lib.exists().where(
            Category.name == field)).scalar()
        if exists:
            self.name.errors.append('Это название уже используется.')
            return False

        return True

    class Meta:
        csrf = True


class TypesForm(CategoryForm):

    def validate_name(self, name):

        field = name.data.strip().lower()
        if not field:
            self.name.errors.append('Поле необходимо заполнить.')
            return False

        exists = db_lib.session.query(db_lib.exists().where(
            Types.name == field)).scalar()
        if exists:
            self.name.errors.append('Такой тип материалов уже есть.')
            return False

        return True

    def validate_fname(self, fname):

        if fname.data is None:
            return True

        field = fname.data.strip().lower()

        exists = db_lib.session.query(db_lib.exists().where(
            Types.name == field)).scalar()
        if exists:
            self.name.errors.append('Такой тип материалов уже есть.')
            return False

        return True

    class Meta:
        csrf = True


class EditHeadingsForm(FlaskForm):

    name = StringField('Имя',
                       validators=[InputRequired(
                           message='Поле должно содержать текст')])
    fname = StringField('Slug')

    class Meta:
        csrf = True

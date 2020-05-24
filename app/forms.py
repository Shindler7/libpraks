"""
Формы приложения.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators
from wtforms.validators import DataRequired, EqualTo, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    """
    Форма авторизации.
    """
    nickname = StringField('Никнейм', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

    def validate_nickname(self, nickname):
        user = User.query.filter_by(nickname=nickname.data).first()
        if user and not user.active:
            raise ValidationError('Учётная запись неактивна.')


class RegForm(FlaskForm):
    """
    Форма регистрации пользователя.
    """
    nickname = StringField('Никнейм', validators=[DataRequired()])
    password1 = PasswordField('Пароль', [
        validators.DataRequired(),
        validators.EqualTo('password2', message='Пароли должны совпадать!')
    ])
    password2 = PasswordField('Пароль повторно', [
        validators.DataRequired()
    ])
    submit = SubmitField('Зарегистрировать')

    def validate_nickname(self, nickname):
        user = User.query.filter_by(nickname=nickname.data).first()
        if user is not None:
            raise ValidationError('Ник занят. Выберите другой, пожалуйста.')

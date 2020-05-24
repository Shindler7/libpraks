"""
Конфигурационные модели для SQL.
"""

from datetime import datetime

from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from app import login_manager

from app import db_lib


class User(UserMixin, db_lib.Model):
    """
    Таблица User - информация о зарегистрированных пользователях.
    """

    __tablename__ = 'User'

    id = db_lib.Column(db_lib.Integer, primary_key=True)
    social_id = db_lib.Column(db_lib.String(64), nullable=True, unique=True)
    nickname = db_lib.Column(db_lib.String(64), nullable=False, unique=True)
    password_hash = db_lib.Column(db_lib.String(128))
    isadmin = db_lib.Column(db_lib.Boolean, default=False)
    active = db_lib.Column(db_lib.Boolean, default=True)

    def set_password(self, password: str) -> None:
        """
        Создание хеш-слепка пароля.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Проверка соответствия хэш-слепка пароля введённому паролю.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User: nickname={self.nickname}, isadmin={self.isadmin}>'

    def __str__(self):
        return self.nickname


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Category(db_lib.Model):
    """
    Таблица Category - содержательная характеристика (Python, sql, django и т.п.).
    Один ко многим.
    """

    __tablename__ = 'Category'

    id = db_lib.Column(db_lib.Integer, primary_key=True)
    name = db_lib.Column(db_lib.String(100), nullable=False, unique=True)
    fname = db_lib.Column(db_lib.String(100))

    content = relationship('Content', backref='Category')

    def __repr__(self):
        return f'<Types(id="{self.id}", name="{self.name}")>'

    def __str__(self):
        return self.name


class Types(db_lib.Model):
    """
    Таблица Types - тип источника (сайт, видео, игра и т.д.).
    Один ко многим.
    """

    __tablename__ = 'Types'

    id = db_lib.Column(db_lib.Integer, primary_key=True)
    name = db_lib.Column(db_lib.String(200), nullable=False, unique=True)
    fname = db_lib.Column(db_lib.String(100))

    content = relationship('Content', backref='Types')

    def __repr__(self):
        return f'<Types(id="{self.id}", name="{self.name}")>'

    def __str__(self):
        return self.name


class Content(db_lib.Model):
    """
    Таблица Content - основные сведения об источнике.
    """

    __tablename__ = 'Content'

    id = db_lib.Column(db_lib.Integer, primary_key=True)
    name = db_lib.Column(db_lib.String(200), nullable=False)
    url = db_lib.Column(db_lib.String(300), nullable=False, unique=True)
    date = db_lib.Column(db_lib.DateTime, nullable=False, default=datetime.now)
    lang = db_lib.Column(db_lib.String(10), nullable=False)
    img_url = db_lib.Column(db_lib.String(200), nullable=True)

    category_id = db_lib.Column(db_lib.Integer(), db_lib.ForeignKey('Category.id'))
    types_id = db_lib.Column(db_lib.Integer(), db_lib.ForeignKey('Types.id'))

    def __repr__(self):
        return f'<Content(name="{self.name}", url="{self.url}", date="{self.date}", lang="{self.lang}")>'

    def __str__(self):
        return self.name



"""
Конфигурационные модели для SQL.

"""

from app import db_lib
from datetime import datetime
from sqlalchemy.orm import relationship


class Category(db_lib.Model):
    """
    Таблица Category - содержательная характеристика (Python, sql, django и т.п.).
    Один ко многим.
    """

    __tablename__ = 'Category'

    id = db_lib.Column(db_lib.Integer, primary_key=True)
    name = db_lib.Column(db_lib.String(100), nullable=False, unique=True)

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
    lang = db_lib.Column(db_lib.String(10), nullable=False, unique=True)

    category_id = db_lib.Column(db_lib.Integer(), db_lib.ForeignKey('Category.id'))
    types_id = db_lib.Column(db_lib.Integer(), db_lib.ForeignKey('Types.id'))

    def __repr__(self):
        return f'<Content(name="{self.name}", url="{self.url}", date="{self.date}", lang="{self.lang}")>'

    def __str__(self):
        return self.name



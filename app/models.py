"""
Конфигурационные модели для SQL.

"""

from app import db_lib
from datetime import datetime


class Category(db_lib.Model):

    __tablename__ = 'Category'

    id = db_lib.Column(db_lib.Integer, primary_key=True)
    name = db_lib.Column(db_lib.String(100), nullable=False, unique=True)
    content = db_lib.relationship('Content', back_populates='Category', lazy='dynamic')

    def __repr__(self):
        return '<Category %r>' % self.name


class Types(db_lib.Model):

    __tablename__ = 'Types'

    id = db_lib.Column(db_lib.Integer, primary_key=True)
    name = db_lib.Column(db_lib.String(200), nullable=False, unique=True)
    content = db_lib.relationship('Content', back_populates='Types', lazy='dynamic')

    def __repr__(self):
        return '<Types %r>' % self.name


class Content(db_lib.Model):

    __tablename__ = 'Content'

    id = db_lib.Column(db_lib.Integer, primary_key=True)
    name = db_lib.Column(db_lib.String(200), nullable=False)
    url = db_lib.Column(db_lib.String(300), nullable=False, unique=True)
    date = db_lib.Column(db_lib.DateTime, nullable=False, default=datetime.now)

    # Связанные поля.
    # backref = при отсутствии взаимной ссылки, back_populates = при взаимной ссылке.
    category_id = db_lib.relationship('Category', back_populates='Content', lazy=False)
    types_id = db_lib.relationship('Types', back_populates='Content', lazy=False)

    def __repr__(self):
        return '<Content %r>' % self.name


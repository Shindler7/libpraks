#! flask\bin\python
"""
Обработка запросов по взаимодействию с SQL.
"""

from app import db_lib
from app.models import Content, Category, Types


def create_all_tables():
    """
    Создаёт таблицы по предустановленным условиям.
    Техническая функция.
    """
    db_lib.create_all()


def add_to_db():
    pass


def read_from_db():
    pass


def remove_from_db():
    pass



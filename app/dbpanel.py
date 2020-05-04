#! flask\bin\python
"""
Обработка запросов по взаимодействию с SQL.
"""

from app import db_lib
from app.models import Content, Category, Types
from datetime import datetime as dt


def tech_all_tables(*, command: str = 'test'):
    """
    Создаёт таблицы по предустановленным условиям.
    Техническая функция.

    Важно! Проверки и подтверждения не осуществляются. Команды исполняются по вызову.

    :param command: 'Test' - действий не производится.
    'Create' - создание таблиц в БД по моделям.
    'Delete' - удаление всех таблиц в БД.
    """
    command = command.lower()
    if not command or command=='test':
        return

    if command == 'create':
        db_lib.create_all()

    if command == 'delete':
        db_lib.drop_all()


def add_to_db(**kwargs) -> bool:
    """
    Добавляет записи из переданного словаря в базу данных.
    :param kwargs: Словарь, содержащий сведения, которые необходимо внести в БД.
    :return: True - при успешном завершении и False при ошибке.
    """

    # ['Empire of Code', 'https://empireofcode.com/', 'en', 'game', ['python']]

    if not kwargs:
        return False

    content = Content(name=kwargs['name'], url=kwargs['url'], date=dt.now().date(),
                      )

    return False


def read_from_db(userquery: dict) -> dict:
    """
    Производит выборку по пользовательскому запросу из базы данных и возвращает в виде словаря.
    :param userquery: Словарь в котором сформулирован запрос.
    :return: Словарь с выборкой по запросу. Если результатов нет, возвращается пустой словарь.
    """
    data_from_bd = {}

    return data_from_bd


def remove_from_db(**kwargs):
    """
    Удаление данных из базы данных. Производит удаление без дополнительного подтверждения.
    Предполагается, что подтверждение было произведено до запроса функции.
    """
    pass


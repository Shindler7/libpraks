#! flask\bin\python
"""
Обработка запросов по взаимодействию с SQL.
"""

from datetime import datetime as dt

from app import db_lib
from app.models import Content, Types, Category
from sqlalchemy.exc import SQLAlchemyError


def tech_all_tables(*, command: str = 'test') -> bool:
    """
    Создаёт таблицы по предустановленным условиям.
    Техническая функция.

    Важно! Проверки и подтверждения не осуществляются. Команды исполняются по вызову.
    Неосторожное использование может привести к потере всей базы данных.

    :param command: 'test' - действий не производится.
    'create.all' - создание таблиц в БД по моделям.
    'delete.all' - удаление всех таблиц в БД.
    """
    command = command.lower()
    if command == 'test':
        return True

    try:
        if command == 'create.all':
            db_lib.create_all()
            return True

        if command == 'delete.all':
            db_lib.drop_all()
            return True

    except SQLAlchemyError:
        return False

    return False


def migrate_to_db() -> bool:
    """
    Временная техническая функция. Экспортирует записи из словаря в БД.
    Использует словарь _dblib.urlbasesource.
    :return: True - при успешном завершении, False - при ошибке.
    """

    from app._dblib import urlbasesource

    if not urlbasesource:
        return False

    for string in urlbasesource.values():
        query_new = {'name': string[0], 'url': string[1], 'lang': string[2], 'types': string[3],
                     'category': string[4][0]}
        if not add_to_db(**query_new):
            return False

    return True


def add_to_db(*, create_types: bool = True, create_category: bool = True, **kwargs) -> bool:
    """
    Добавляет записи из переданного словаря в базу данных.
    :param create_types: Если переданный тип отсутствует, создать и связать с ним запись.
    False - не выполнять запрос.
    :param create_category: Если переданная категория отсутствует, создать и связать с ним запись.
    False - не выполнять запрос.
    :param kwargs: Словарь, содержащий сведения, которые необходимо внести в БД.
    :return: True - при успешном завершении и False при ошибке.
    """

    # {'name='Empire of Code', url='http://empireofcode.com,
    # lang='en', types='game', category='Python'}

    if not kwargs:
        return False

    type_in = Types.query.filter_by(name=kwargs['types']).first()
    category_in = Category.query.filter_by(name=kwargs['category']).first()
    if not type_in:
        if create_types:
            type_in = Types(name=kwargs['types'])
            db_lib.session.add(type_in)
            db_lib.session.commit()
        else:
            return False

    if not category_in:
        if create_category:
            category_in = Category(name=kwargs['category'])
            db_lib.session.add(category_in)
            db_lib.session.commit()
        else:
            return False

    content = Content(name=kwargs['name'],
                      url=kwargs['url'],
                      lang=kwargs['lang'],
                      # date - TODO: обработка переданной даты.
                      types_id=type_in.id,
                      category_id=category_in.id
                      )

    db_lib.session.add(content)
    db_lib.session.commit()
    return True


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

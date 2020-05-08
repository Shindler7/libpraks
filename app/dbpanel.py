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


class DBWork:

    category = None
    types = None
    category_list = None
    types_list = None
    lang_list = None

    def __init__(self, *, reload=False):
        if self.category is None or self.types is None or reload:
            self.category = Category.query.all()
            self.types = Types.query.all()
            self.category_list = self.get_category_name()
            self.types_list = self.get_types_name()
            self.lang_list = self.get_lang_list()

    def get_category_name(self) -> dict:
        if self.category_list:
            return self.category_list
        return {ids.name: ids.id for ids in self.category}

    def get_types_name(self, *, category=None) -> dict:
        if category is not None:
            types = []
            for ty in db_lib.session.query(Content.types_id).filter(Content.category_id==category).all():
                if ty.types_id not in types:
                    types.append(ty.types_id)
            return types.sort()

        if self.types_list:
            return self.types_list
        return {ids.fname: ids.id for ids in self.types}

    def get_lang_list(self) -> list:
        if self.lang_list:
            return self.lang_list
        # lang = Content.query.distinct(Content.lang).order_by(Content.lang).all()
        lang = db_lib.session.query(Content.lang).distinct()

        return [lg.lang for lg in lang]


def get_content(**key_dict):
    # key_dict = {'tag': [], 'lang': [], 'type'}

    content = Content.query

    if key_dict['tag']:
        content = content.filter(Content.category_id.in_(key_dict['tag']))
    if key_dict['type']:
        content = content.filter(Content.types_id.in_(key_dict['type']))
    if key_dict['lang']:
        content = content.filter(Content.lang.in_([key_dict['lang']]))

    return content.order_by(Content.types_id).all()


def read_tables_from_db(**kwargs) -> dict:
    pass


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

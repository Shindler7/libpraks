"""
Обработка запросов по взаимодействию с SQL.
"""

# https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_filter_operators.htm

from sqlalchemy.exc import SQLAlchemyError

from app import db_lib
from app.exc import DBArgumentsError, DBNoTableOrValue
from app.models import Category, Content, Types, User


class DBWork:
    """
Класс агрегирует данные таблиц Types и Category,
чтобы минимизировать обращение к БД за данными,
которые обладают статичностью и часто востребованы.
"""

    category = None
    types = None

    def __init__(self):
        self.category = None
        self.types = None

    @classmethod
    def get_all_key_category(cls, *, reverse=False) -> dict:
        """
        Возвращает словарь со всеми категориями в БД.
        :param reverse: Разворачивает словарь (меняет ключи и значения
        местами).
        """
        if cls.category is None:
            cls.category = Category.query.all()
        if reverse:
            return {ids.id: ids.name for ids in cls.category}

        return {ids.name: ids.id for ids in cls.category}

    @property
    def get_list_category(self) -> dict:
        """
        Возвращает словарь категорий в режиме свойства.
        """
        return self.get_all_key_category()

    @property
    def get_list_category_reverse(self) -> dict:
        """
        Возвращает словарь категорий в режиме свойства.
        Представлен в режиме reverse.
        """
        return self.get_all_key_category(reverse=True)

    @classmethod
    def get_all_key_types(cls, *, reverse=False) -> dict:
        """
        Возвращает словарь со всеми типами в БД.
        :param reverse: Разворачивает словарь (меняет местами ключи
        и значения).
        """
        if cls.types is None:
            cls.types = Types.query.all()
        if reverse:
            return {ids.id: ids.name for ids in cls.types}

        return {ids.name: ids.id for ids in cls.types}

    @property
    def get_list_types(self) -> dict:
        """
        Возвращает словарь типов в режиме свойства.
        """
        return self.get_all_key_types()

    @property
    def get_list_types_reverse(self) -> dict:
        """
        Возвращает словарь типов в режиме свойства.
        Представлен реверсионно.
        """
        return self.get_all_key_types(reverse=True)

    @property
    def get_list_language(self) -> list:
        """
        Возвращает список языков из базы данных.
        """
        # FIXME: возвращается не список для итерации [(...,), (...,)]
        return db_lib.session.query(Content.lang).distinct().all()

    @classmethod
    def get_all_category(cls):
        return Category.query.order_by(Category.name).all()

    @classmethod
    def get_all_content(cls) -> list:
        """
        Возвращает содержимое всей таблицы Content.
        """
        return Content.query.all()

    @classmethod
    def get_choices_types(cls, *, category: str) -> list:
        """
        Возвращает типы, соответствующие указанной категории.
        :param category: Категория для которой следует подобрать типы (Types).
        Если пусто, возвращает все типы (Types)
        """
        choices_types = list()
        base_types = cls.get_all_key_types(reverse=True)
        query = db_lib.session.query(Content.types_id)
        if category:
            # FIXME: найти способ оптимизировать SQL-запрос.
            category = Category.query.filter_by(name=category).first()
            query = query.filter(Content.category_id == category.id)

        query = query.distinct()
        for typ in query:
            choices_types.append(base_types[typ.types_id])
        choices_types.sort()

        return choices_types


class DBExecute(DBWork):

    def __init__(self):
        super().__init__()

    def add_to_db(self, *, create_types: bool = True,
                  create_category: bool = True, **kwargs):
        """
        Добавляет записи из переданного словаря в базу данных.
        :param create_types: Если переданный тип отсутствует, создать и
        связать с ним запись.
        False - не выполнять запрос.
        :param create_category: Если переданная категория отсутствует, создать
        и связать с ним запись. False - не выполнять запрос.
        :param kwargs: Словарь, содержащий сведения, которые необходимо
        внести в БД.
        :return: True - при успешном завершении и False при ошибке.
        """

        if not kwargs:
            raise DBArgumentsError

        type_in = Types.query.filter_by(name=kwargs['types']).first()
        category_in = Category.query.filter_by(name=kwargs['category']).first()

        if not type_in:
            if create_types:
                type_in = Types(name=kwargs['types'])
                db_lib.session.add(type_in)
                db_lib.session.commit()
            else:
                raise DBNoTableOrValue(kwargs['types'])

        if not category_in:
            if create_category:
                category_in = Category(name=kwargs['category'])
                db_lib.session.add(category_in)
                db_lib.session.commit()
            else:
                raise DBNoTableOrValue(kwargs['category'])

        content = Content(name=kwargs['name'],
                          url=kwargs['url'],
                          lang=kwargs['lang'],
                          # date - TODO: обработка переданной даты.
                          types_id=type_in.id,
                          category_id=category_in.id
                          )

        db_lib.session.add(content)
        db_lib.session.commit()

    def add_category(self, *, name: str, fname: str = None) -> bool:
        """
        Добавляет новую категорию в базу.
        :param name: Поле name в базе (название).
        :param fname: Поле fname в базе (резервное). Можно None.
        :return: True, если успешно, False при ошибке.
        """

        name = name.strip().lower()
        if fname is not None:
            fname = fname.strip().lower()

        try:
            category = Category(name=name, fname=fname)
            db_lib.session.add(category)
            db_lib.session.commit()
        except SQLAlchemyError:
            return False
        else:
            return True

    def add_types(self, *, name: str, fname: str = None) -> bool:
        """
        Добавляет новый тип в базу.
        :param name: Поле name в базе (название).
        :param fname: Поле fname в базе (резервное). Можно None.
        :return: True, если успешно, False при ошибке.
        """

        name = name.strip().lower()
        if fname is not None:
            fname = fname.strip().lower()

        try:
            types = Types(name=name, fname=fname)
            db_lib.session.add(types)
            db_lib.session.commit()
        except SQLAlchemyError:
            return False
        else:
            return True

    def get_content(self, **key_dict) -> list:
        """
        Производит выборку по пользовательскому запросу из базы данных
        и возвращает в виде словаря.
        :param {dict} key_dict: Словарь в котором сформулирован запрос.
        key_dict = {'tag': [], 'lang': [], 'type'}
        :return: Список с выборкой по запросу.
        """

        content = Content.query
        if key_dict.get('full', False):
            return content.order_by(Content.id.desc()).all()

        if key_dict.get('tag', ''):
            content = content.filter(Content.category_id.in_(key_dict['tag']))
        if key_dict.get('type', ''):
            content = content.filter(Content.types_id.in_(key_dict['type']))
        if key_dict.get('lang', ''):
            content = content.filter(Content.lang.in_([key_dict['lang']]))

        return content.order_by(Content.types_id, Content.name).all()

    def change_user_status(self, field: str, *, user_id: int) -> bool:
        """
        Оборачивает значения active и isadmin. Возвращает True при успехе.
        :param field: active или isadmin - поля в модели.
        :param user_id: ID пользователя.
        """

        try:
            user = User.query.filter(User.id == user_id).first()

            if field == 'active':
                user.active = not user.active
                db_lib.session.commit()

            if field == 'isadmin':
                user.isadmin = not user.isadmin
                db_lib.session.commit()

        except SQLAlchemyError:
            return False
        else:
            return True

    def delete_category_or_types(self, field: str, *, data_id: int):
        """
        Удаляет категорию или тип, в зависимости от переданной команды.
        :param field: category or types.
        :param data_id: ID категории или типа.
        :return: True при успехе и False, если что-то не получилось.
        """

        method = {'category': Category, 'types': Types}
        if field not in method.keys():
            return False

        try:
            method[field].query.filter(method[field].id == data_id).delete()
            db_lib.session.commit()
        except SQLAlchemyError:
            return False
        else:
            return True

    def delete_user(self, *, user_id: int) -> bool:
        """
        Удаление пользователя из базы по id.
        :param user_id: ID пользователя для удаления.
        """
        try:
            User.query.filter(User.id == user_id).delete()
            db_lib.session.commit()
        except SQLAlchemyError:
            return False
        else:
            return True

    def del_from_db(self, *, id_n: int):
        """
        Удаляет конкретную запись из БД. При неудаче возвращает False.
        :param id_n: ID записи для удаления.
        """

        Content.query.filter(Content.id == id_n).delete()
        db_lib.session.commit()


def tech_bd_services(*, command: str) -> bool:
    """
    Внутренняя техническая функциия для обслуживания системных запросов к БД.

    Важно! Проверки и подтверждения не осуществляются. Команды исполняются по
    вызову. Неосторожное использование может привести к потере
    всей базы данных.

    :param command:'create.all' - создание таблиц в БД по моделям.
    'delete.all' - удаление всех таблиц в БД.
    :return: True - если задача успешно исполнена, False в обратном случае.
    """

    try:
        if command == 'create.all':
            db_lib.create_all()
            return True

        if command == 'delete.all':
            db_lib.drop_all()
            return True

        if command == 'save.urlbase':
            dbe = DBExecute()

            from app.dblib import urlbasesource
            if not urlbasesource:
                return False
            for string in urlbasesource.values():
                query_new = dict(name=string[0],
                                 url=string[1],
                                 lang=string[2],
                                 types=string[3],
                                 category=string[4]
                                 )
                if not dbe.add_to_db(**query_new):
                    return False

            return True

    except SQLAlchemyError:
        return False

    return False

"""
Обработка запросов по взаимодействию с SQL.
"""

# https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_filter_operators.htm

from sqlalchemy.exc import SQLAlchemyError

from app import db_lib
from app.models import Types


class QA:
    """
    Класс-ассистент, содержащий специальные технические методы,
    преобразующий запросы базы в нужные форматы данных.
    """

    @classmethod
    def get_types_by(cls, *, category: str) -> dict:
        """
        Формирует словарь типов данных по переданной категории.
        Формат: {id типа: name типа}
        :param category: Категория (Category)
        """
        types = Types.manager.get_by(category=category)

        return {type_.id: type_.name for type_ in types}


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

    except SQLAlchemyError:
        return False

    return False

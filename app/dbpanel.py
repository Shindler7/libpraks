"""
Обработка запросов по взаимодействию с SQL.
"""

# https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_filter_operators.htm

from sqlalchemy.exc import SQLAlchemyError

from app import db_lib


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

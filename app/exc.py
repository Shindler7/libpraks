"""
Исключения применяемые в Lib Praktikum.
"""


class LibBaseError(Exception):
    pass


class DataBaseError(LibBaseError):
    pass


class DBArgumentsError(DataBaseError):

    def __str__(self):
        return 'Отсутствуют ожидаемые аргументы.'


class DBNoTableOrValue(DataBaseError):

    def __str__(self):
        return 'Отсутствует искомая таблица или значение.'

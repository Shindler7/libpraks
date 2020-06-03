"""
Исключения применяемые в Lib Praktikum.
"""


class LibBaseError(Exception):

    def __init__(self, message: str = None):
        self.message = message
        if message is None:
            self.message = 'LibBaseError'

    def __str__(self):
        return self.message

class DataBaseError(LibBaseError):
    pass


class DBArgumentsError(DataBaseError):

    def __init__(self, message: str = None):
        self.message = message
        if message is None:
            self.message = 'Отсутствуют ожидаемые аргументы.'

    def __str__(self):
        return self.message


class DBNoTableOrValue(DataBaseError):

    def __init__(self, message: str = None):
        self.message = message
        if message is None:
            self.message = 'Отсутствует искомая таблица или значение.'

    def __str__(self):
        return self.message

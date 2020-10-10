"""
Компонентные поддерживающие декораторы.
"""
from functools import wraps
from time import time


def runtime(decorate_func):
    """
    Декоратор замера времени исполнения функции.
    """

    @wraps(decorate_func)
    def wrapper(*args, **kwargs):
        start = int(round(time() * 1000))

        try:
            return decorate_func(*args, **kwargs)
        finally:
            end = int(round(time() * 1000)) - start
            print(f'Время работы: {end if end > 0 else 0} мс')

    return wrapper

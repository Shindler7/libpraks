"""
Дополнительные утилиты
"""
from werkzeug.routing import BaseConverter


class DictConverter(BaseConverter):

    def to_python(self, key, value):
        return value.split('+')

    def to_url(self, values):
        return '+'.join(BaseConverter.to_url(value)
                        for value in values)
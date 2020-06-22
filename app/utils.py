# import os
import random
import string

from urllib.parse import urlparse
from app.models import Content

STRING_LENGTH = 6


def random_string(string_length=STRING_LENGTH) -> str:
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


def get_screen_name(id):
    obj = Content.query.filter_by(id=id).first()
    url = obj.url
    url_parse = urlparse(url)
    url_parse = url_parse.netloc
    screen_suffix = random_string()
    screen_name = url_parse.replace('.', '_') + '_' + screen_suffix + '.png'
    return screen_name

#
# def get_full_path(name):
#     img_static_path = os.path.join('static', 'img', 'screenshot', name)
#     dirname = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(dirname, img_static_path)
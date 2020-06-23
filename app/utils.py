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
    all_screen_names = Content.query.with_entities(Content.img_url)
    if screen_name in all_screen_names:
        get_screen_name(id)
    return screen_name

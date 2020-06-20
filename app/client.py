import os
import random
import string
import sys

import requests
import shutil

from urllib.parse import urlparse
from app import application, db_lib
from app.models import Content


def random_string(string_length=8) -> str:
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


def get_url_path(url):
    static_path = application.config['IMAGES_PATH'][0]
    url_parse = urlparse(url)
    img_name_suffix = random_string()
    img_name = url_parse.netloc + '_' + img_name_suffix + '.png'
    img_path = os.path.join(static_path, img_name)
    all_img_path = Content.query.with_entities(Content.img_url)
    if img_path in all_img_path:
        get_url_path(url)
    return img_path


def get_image(id=None, url=None):
    server = application.config['SCREEN_SERVER']
    params = {'url': url}
    path = get_url_path(url)
    dirname = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(dirname, path)

    r = requests.get(server, params=params, stream=True)
    if r.status_code == 200:
        with open(full_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

    last_obj = Content.query.filter(Content.id == id).first()
    if last_obj:
        last_obj.img_url = path
        db_lib.session.add(last_obj)
        db_lib.session.commit()


if __name__ == '__main__':
    args = sys.argv
    get_image(id=args[1], url=args[2])

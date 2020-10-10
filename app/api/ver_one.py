"""
Инфраструктура API ver 1.0
"""

from urllib.parse import urljoin

from app import application
from app.models import Types
from app.views import load_screen


@application.route('/v1/data', methods=['GET'])
def api_index():
    """
    Возвращает JSON с данными, структурированными по типам.
    """
    data = {}
    for elem in Types.manager.get_all():
        if elem.content.count() == 0:
            continue

        types_name = elem.name
        types_content = {types_name: {}}

        for content_data in elem.content.all():
            url_for = load_screen(content_data.img_url,
                                  only_url=True
                                  ).replace('\\', '/')
            url_for = urljoin('https://coralboat.online', url_for)

            types_content[types_name].update(
                {content_data.name: {
                    'url': content_data.url,
                    'img_url': url_for,
                    'lang': content_data.lang
                }
                })

        data.update(types_content)

    return data

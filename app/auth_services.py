import base64

from flask import redirect
from requests import get, post

from app import application


def base64_decode_string(id, secret):
    """
    Функция кодирует client_id и secret_key для последующей передачи их в
    заголовке POST запроса при авторизации на oauth.yandex.ru.
    """
    base64_message = id + ':' + secret
    base64_bytes = base64_message.encode('utf-8')
    message_bytes = base64.b64encode(base64_bytes)
    message = message_bytes.decode('utf-8')
    return message


def get_yandex_oauth_code(redirect_url):
    """
    Первый этап авторизации — получение кода, которые нужно вернуть обратно на
    сервер oauth.yandex.ru для получения токена.
    """
    url = application.config['YANDEX_AUTHORIZE_URL'] + 'authorize'
    params = {
        'response_type': 'code',
        'client_id': application.config['YANDEX_CLIENT'],
        'redirect_uri': redirect_url,
    }
    response = get(url, params=params)
    return redirect(response.url, 302)


def get_yandex_user_profile(token):
    """
    Запрос учетных данных пользователя (nickname, social_id) по полученному
    ранее OAuth-токену.
    """
    url = application.config['YANDEX_LOGIN_URL']
    params = {
        'format': 'json',
    }
    headers = {
        'Authorization': 'OAuth ' + token
    }
    response = get(url, params=params, headers=headers)
    return response.json()


def yandex_oauth(code):
    """
    Второй этап авторизации — по полученному ранее коду запрашиваем
    OAuth-токен. При помощи токена получаем данные учетной записи пользователя.
    """
    url = application.config['YANDEX_AUTHORIZE_URL'] + 'token'
    auth_decode_string = base64_decode_string(
        application.config['YANDEX_CLIENT'],
        application.config['YANDEX_TOKEN']
    )
    headers = {
        'Authorization': 'Basic ' + auth_decode_string,
        'Content-type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,

    }
    response = post(url, data=data, headers=headers)
    token = response.json().get('access_token')

    yandex_user_profile = get_yandex_user_profile(token)
    nickname = yandex_user_profile.get('login')
    social_id = yandex_user_profile.get('id')

    return nickname, social_id

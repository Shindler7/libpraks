import os

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    # Основные настройки
    DEBUG = True if os.environ.get('FLASK_ENV') == 'development' else False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SEND_FILE_MAX_AGE_DEFAULT = 0
    IMAGES_PATH = ['static']

    # База данных
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DBHOST = 'server216.hosting.reg.ru' if DEBUG else 'localhost'
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://' \
                              f'{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}' \
                              f'@{DBHOST}/u0988708_corallib'

    # Авторизация OAuth
    YANDEX_CLIENT = os.getenv('YANDEX_CLIENT')
    YANDEX_TOKEN = os.getenv('YANDEX_TOKEN')

    # Авторизационные ключи ReCaptcha2
    RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')
    RECAPTCHA_PARAMETERS = {'hl': 'ru'}
    RECAPTCHA_DATA_ATTRS = {'theme': 'dark', 'size': 'normal'}

    # Конфигурация screenshoter
    SCREEN_SERVER = 'http://djap.fun/'
    SCREEN_SERVER_SECRET_KEY = os.getenv('SCREEN_SERVER_SECRET_KEY')
    SCREEN_URL_ROOT = 'img'
    SCREEN_URL_FOLDER = 'screenshot'

    UPLOAD_FOLDER = 'app/static/img/screenshot'
    STORAGE_PATH = 'static/img/screenshot/'
    PROJECT_HOST = 'https://7cf41d427274.ngrok.io'

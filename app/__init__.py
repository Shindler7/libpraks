#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask import Flask
from config import Config
from flask_sslify import SSLify
from flask_mobility import Mobility
from flask_bootstrap import Bootstrap
from flask_nav import Nav

application = Flask(__name__)
application.config.from_object(Config)
sslify = SSLify(application)  # Подключение SSL
Mobility(application)  # Мобильная версия
Bootstrap(application)  # Bootstrap
nav = Nav()
nav.init_app(application)

from app import routes

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000)

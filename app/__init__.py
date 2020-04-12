#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask import Flask
from config import Config
from flask_sslify import SSLify
from flask_mobility import Mobility
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_sqlalchemy import SQLAlchemy

# Flask
application = Flask(__name__)
application.config.from_object(Config)
# Подключение (обслуживание) SSL (https://)
sslify = SSLify(application)  
# Мобильная версия
Mobility(application)  
# Bootstrap
Bootstrap(application)  
nav = Nav()
nav.init_app(application)
# SQLAlchemy
sql_user_lib = SQLAlchemy(application)

from app import routes

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000)

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask import Flask
from flask_images import Images
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy as SQLA
from flask_sslify import SSLify
from flask_wtf.csrf import CSRFProtect

from config import Config

# *** временно выключено ***
# import logging
# logging.basicConfig(filename='libprakt.log', level=logging.INFO)

# Flask
application = Flask(__name__)
application.config.from_object(Config)

# Подключение (обслуживание) SSL
sslify = SSLify(application)

# SQLAlchemy + Migrate
db_lib = SQLA(application)
migrate = Migrate(application, db_lib)

# Login
login_manager = LoginManager(application)
login_manager.login_view = 'login'

# CSRF
csrf = CSRFProtect(application)

# Flask image
images = Images(application)


from app import views  # noqa
from app import admin  # noqa


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000)

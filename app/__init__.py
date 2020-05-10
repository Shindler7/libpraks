#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask import Flask
from config import Config
from flask_sslify import SSLify
from flask_sqlalchemy import SQLAlchemy as SQLA
from flask_migrate import Migrate

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


from app import routes

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000)

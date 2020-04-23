#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask import Flask
from config import Config
from flask_sslify import SSLify
from flask_sqlalchemy import SQLAlchemy

import logging

logging.basicConfig(filename='libprakt.log', level=logging.INFO)

# Flask
application = Flask(__name__)
application.config.from_object(Config)

# Подключение (обслуживание) SSL (https://)
sslify = SSLify(application)  

# SQLAlchemy * ВРЕМЕННО ОТКЛЮЧЕНО *
sql_user_lib = SQLAlchemy(application)

from app import routes

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000)

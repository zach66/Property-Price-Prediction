import os

DEBUG = True
LOGGING_CONFIG = "config/logging/local.conf"
PORT = 1996
APP_NAME = "house-price"
SQLALCHEMY_TRACK_MODIFICATIONS = True
HOST = "0.0.0.0"
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100

# Connection string
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

if SQLALCHEMY_DATABASE_URI is not None:
    pass
else:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/house_sale.db'


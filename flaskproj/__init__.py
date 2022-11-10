import os

import psycopg2
from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_babelex import Babel
from flask_ckeditor import CKEditor


load_dotenv(find_dotenv())
app = Flask(__name__)
babel = Babel(app)
ckeditor = CKEditor(app)

app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://a-v-tor@localhost/mybase"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"
app.config['CSRF_ENABLED'] = True 
app.config['MAIL_SERVER'] = 'smtp.yandex.ru'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('mail')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('mail')
app.config['MAIL_PASSWORD'] = os.getenv('psw_mail')
app.config['CKEDITOR_PKG_TYPE'] = 'base'
app.config['CKEDITOR_WIDTH'] = 880





db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)


from . import admin, views

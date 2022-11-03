import os

import psycopg2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(12)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://a-v-tor@localhost/mybase"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"
app.config['CSRF_ENABLED'] = True  # WTF_CSRF_ENABLED  ???


db = SQLAlchemy(app)
migrate = Migrate(app, db)

from . import admin, views

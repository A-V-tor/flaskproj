import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
import psycopg2


app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(12)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://a-v-tor@localhost/mybase"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, name='shop', template_mode='bootstrap4')


db = SQLAlchemy(app)

from . import views

import datetime
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from flaskproj import db


class Userprofile(db.Model, UserMixin):
    """Модель юзера"""

    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    psw = db.Column(db.String(300))
    data_registered = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    user_bascet = relationship("Bascet", cascade="all, delete")
    user_order = relationship("Orderuser", cascade="all, delete")
    user_post = relationship("UserPosts", cascade="all, delete")

    def __str__(self):
        return self.name
    

class Product(db.Model):
    """Модель товара"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    image = db.Column(db.String(100))
    price = db.Column(db.Float)
    product_story = db.Column(db.String(500))
    amount = db.Column(db.Integer)
    product_bascet = relationship("Bascet", cascade="all, delete")
    product_trending = relationship("TrendingProduct")


class Bascet(db.Model):
    """Модель корзины товаров юзера"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("userprofile.id"))
    product_id = db.Column(db.Integer, ForeignKey("product.id"))


class Orderuser(db.Model):
    """Модель исполненых заказов"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("userprofile.id"))
    date = db.Column(db.DateTime)
    list_product = db.Column(db.JSON)
    order_price = db.Column(db.Integer)
    invoice_id = db.Column(db.String(255))


class TrendingProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, ForeignKey("product.id"))
    item = db.Column(db.Integer)


class UserPosts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    title = db.Column(db.String(50))
    body = db.Column(db.String(250))
    user_name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, ForeignKey("userprofile.id"))


db.create_all()

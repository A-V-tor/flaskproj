from flaskproj import db
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from flask_login import UserMixin


class Userprofile(db.Model, UserMixin):
    """Модель юзера"""

    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    psw = db.Column(db.String(300))
    user_bascet = relationship("Bascet")
    user_card = relationship("Usercard")
    user_order = relationship("Orderuser")


class Product(db.Model):
    """Модель товара"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    image = db.Column(db.String(100))
    price = db.Column(db.Integer)
    product_story = db.Column(db.String(500))
    amount = db.Column(db.Integer)
    product_bascet = relationship("Bascet", cascade="all, delete")
    product_trending = relationship("TrendingProduct")


class Bascet(db.Model):
    """Модель корзины товаров юзера"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("userprofile.id"))
    product_id = db.Column(db.Integer, ForeignKey("product.id"))


class Usercard(db.Model):
    """Модель пользовательских карт оплаты"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("userprofile.id"))
    surname = db.Column(db.String(80))
    firstname = db.Column(db.String(80))
    patronymic = db.Column(db.String(80))
    number_card = db.Column(db.String(20), unique=True)
    validity = db.Column(db.String(5))
    secret_code = db.Column(db.String(4))
    balance = db.Column(db.Integer)


class Orderuser(db.Model):
    """Модель исполненых заказов"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("userprofile.id"))
    date = db.Column(db.DateTime)
    list_product = db.Column(db.JSON)
    order_price = db.Column(db.Integer)


class TrendingProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, ForeignKey("product.id"))
    item = db.Column(db.Integer)


db.create_all()

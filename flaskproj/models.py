from flaskproj import db
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class Userprofile(db.Model):
    '''Модель юзера'''
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    psw = db.Column(db.String(300))
    user_bascet = relationship('Bascet')


class Product(db.Model):
    '''Модель товара'''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    image = db.Column(db.String(100))
    price = db.Column(db.Integer)
    product_story = db.Column(db.String(500))
    amount = db.Column(db.Integer)
    product_bascet = relationship('Bascet')


class Bascet(db.Model):
    '''Модель корзины товаров юзера'''
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('userprofile.id'))
    product_id = db.Column(db.Integer, ForeignKey('product.id'))

db.create_all()




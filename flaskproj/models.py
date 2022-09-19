from flaskproj import db


class Userprofile(db.Model):
    '''Модель юзера'''
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    psw = db.Column(db.String(300))


class Product(db.Model):
    '''Модель товара'''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    image = db.Column(db.String(100))
    price = db.Column(db.String(50))
    product_story = db.Column(db.String(500))
    amount = db.Column(db.String(60))

db.create_all()




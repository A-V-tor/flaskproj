from flaskproj import db


class Userprofile(db.Model):
    '''Модель юзера'''
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    psw = db.Column(db.String(300))

db.create_all()




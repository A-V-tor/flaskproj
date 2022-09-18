import os
from flask import Flask, render_template, request, url_for
from forms import FormRegAvt
from flask_sqlalchemy import SQLAlchemy
import psycopg2



app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://a-v-tor@localhost/mybase'

db = SQLAlchemy(app)


class User(db.Model):
    '''Модель юзера'''
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(100))
    name = db.Column(db.String(100))
    psw = db.Column(db.String(300))

db.create_all()

@app.route('/', methods=['POST', 'GET'])
def index_registration():
    '''Обработка регистрации'''
    forma = FormRegAvt()
    if forma.validate_on_submit():
        try:
            u = User(mail=forma.email.data, name=forma.name.data, psw=forma.psw.data)
            db.session.add(u)
            db.session.commit()
            print('YES')
        except:
            print('ОШИБКА ЗАПИСИ')
    return render_template('forma_registration.html', forma=forma, title='Регистрация')


@app.route('/1', methods=['POST', 'GET'])
def index_avtorization():
    '''Обработка авторизации'''
    forma = FormRegAvt()
    if forma.validate_on_submit():
        print(forma.name.data)
    return render_template('forma_avtorization.html', forma=forma, title='Авторизация')





if __name__ == '__main__':
    app.run(debug=True)
from .forms import FormRegAvt
from flask import render_template, request, url_for
from flaskproj import app,db
from .models import Userprofile


@app.route('/', methods=['POST', 'GET'])
def index_registration():
    '''Обработка регистрации'''
    forma = FormRegAvt()
    if forma.validate_on_submit():
        try:
            u = Userprofile(mail=forma.email.data, name=forma.name.data, psw=forma.psw.data)
            db.session.add(u)
            db.session.commit()
            print('ЮЗЕР ЗАЛОГИНИН')
        except:
            print('ОШИБКА ЗАПИСИ ЛОГИНА')
    return render_template('forma_registration.html', forma=forma, title='Регистрация')


@app.route('/1', methods=['POST', 'GET'])
def index_avtorization():
    '''Обработка авторизации'''
    forma = FormRegAvt()
    if forma.validate_on_submit():
        print(forma.name.data)
    return render_template('forma_avtorization.html', forma=forma, title='Авторизация')






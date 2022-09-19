from flask_bootstrap import Bootstrap
from flask import render_template, request, url_for
from .forms import FormRegAvt
from flaskproj import app,db
from .models import Userprofile


Bootstrap(app)


@app.route('/', methods=['POST', 'GET'])
def index_main():
    return render_template('main.html', title='Главная страница')


@app.route('/registration', methods=['POST', 'GET'])
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
    else:
        h = Userprofile.query.filter_by(name='admin').first()
        print(h)
        
    return render_template('forma_registration.html', forma=forma, title='Регистрация')


@app.route('/avtorization', methods=['POST', 'GET'])
def index_avtorization():
    '''Обработка авторизации'''
    forma = FormRegAvt()
    if forma.validate_on_submit():
        print(forma.name.data)
    return render_template('forma_avtorization.html', forma=forma, title='Авторизация')






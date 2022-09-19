import re
from flask_bootstrap import Bootstrap
from flask import render_template, request, url_for, redirect, flash, session, abort
from .forms import FormReg, FormAvt
from flaskproj import app,db
from .models import Userprofile


Bootstrap(app)

@app.route('/', methods=['POST', 'GET'])
def index_main():
    '''Обработка главной страницы'''
    if 'username' in session:
        print('SESSIN YES')
        username = session['username']
        return render_template('main.html', title='Главная страница', name=username)
    return render_template('main.html', title='Главная страница')


@app.route('/registration', methods=['POST', 'GET'])
def index_registration():
    '''Обработка регистрации'''
    forma = FormReg()
    if 'username'  in session:
        return redirect(url_for('index_shopping_basket', username=session['username']))
    if forma.validate_on_submit():
        try:
            user = Userprofile(mail=forma.email.data, name=forma.name.data, psw=forma.psw.data)
            db.session.add(user)
            db.session.commit()
            print('ЮЗЕР ЗАЛОГИНИН')
        except:
            flash('Пользователь с таким адресом уже есть!', category='error')
            print('ОШИБКА ЗАПИСИ ЛОГИНА')
        return redirect(url_for('index_avtorization')) 
    return render_template('forma_registration.html', forma=forma, title='Регистрация')


@app.route('/avtorization', methods=['POST', 'GET'])
def index_avtorization():
    '''Обработка авторизации'''
    forma = FormAvt()
    if 'username'  in session:
        return redirect(url_for('index_shopping_basket', username=session['username']))
    if forma.validate_on_submit():
        print('forma arbeit')
        datauser = Userprofile.query.filter_by(name=forma.name.data,psw=forma.psw.data).first()
        print(datauser)
        if datauser:
            session['username'] = datauser.name
            return redirect(url_for('index_shopping_basket', username=session['username']))
        else:
            flash('Неверное имя или пароль!', category='error')

    return render_template('forma_avtorization.html', forma=forma, title='Авторизация')


@app.route('/basket/<username>', methods=['POST', 'GET'])
def index_shopping_basket(username):
    if 'username' not in session or session['username'] != username:
        print('hujnj')
        return redirect(url_for('index_avtorization'))
    return render_template('basket.html', name=username)






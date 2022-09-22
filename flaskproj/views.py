from flask_bootstrap import Bootstrap
from flask import render_template, request, url_for, redirect, flash, session, abort
from .forms import FormReg, FormAvt
from flaskproj import app,db
from .models import Userprofile, Product, Bascet


Bootstrap(app)

@app.route('/', methods=['POST', 'GET'])
def index_main():
    '''Обработка главной страницы'''
    data_product = Product.query.filter_by().all()
    print(data_product)
    if 'username' in session:
        username = session['username']
        bascet = True
        if request.method == 'POST':
            name_product = [i for i in request.form.values()]
            print('button',*name_product)
            bascet_write = Bascet(user_id=int(session['name_id']),product_id=int(*name_product))
            db.session.add(bascet_write)
            db.session.commit()
        return render_template('main.html', title='Главная страница', name=username, data_product=data_product, bascet=bascet)
    return render_template('main.html', title='Главная страница', data_product=data_product)


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
            session['mail'] = datauser.mail
            session['username'] = datauser.name
            session['name_id'] = datauser.id
            return redirect(url_for('index_shopping_basket', username=session['username']))
        else:
            flash('Неверное имя или пароль!', category='error')
    return render_template('forma_avtorization.html', forma=forma, title='Авторизация')


@app.route('/basket/<username>', methods=['POST', 'GET'])
def index_shopping_basket(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('index_avtorization'))
    else:
        mail = session['mail']
        personality = [i for i in Bascet.query.filter_by(user_id=session['name_id']).all()]
        data_product = [Product.query.filter_by(id=i.product_id).first() for i in personality]
        return render_template('basket.html', name=username, mail=mail, data_product=data_product)


@app.errorhandler(404)
def pageNot(error):
    return redirect(url_for('index_avtorization'))






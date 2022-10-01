from flask_bootstrap import Bootstrap
from flask import render_template, request, url_for, redirect, flash, session, abort
from .forms import FormReg, FormAvt, FormAddCard
from flaskproj import app,db
from .models import Userprofile, Product, Bascet, Usercard, Orderuser
from .other import add_balance, get_item, get_data_product_bascet_and_card, get_data_list_product_and_total_price, set_new_amount, UserLogin
#from flask_login import LoginManager, login_user, login_required, current_user


Bootstrap(app)
#login_manager = LoginManager(app)


@app.route('/', methods=['POST', 'GET'])
def index_main():
    '''Обработка главной страницы'''
    data_product = Product.query.filter_by().all()
    if 'username' in session:
        username = session['username']
        bascet = True
        if request.method == 'POST':
            name_product = [i for i in request.form.values()]
            print('button',*name_product)
            limit_entries = Bascet.query.filter_by(user_id=int(session['name_id']),product_id=int(*name_product)).all()
            if len(limit_entries) > 0:
                return render_template('main.html', title='Главная страница', name=username, data_product=data_product, bascet=bascet, username = session['username'])
            bascet_write = Bascet(user_id=int(session['name_id']),product_id=int(*name_product))
            db.session.add(bascet_write)
            db.session.commit()
        return render_template('main.html', title='Главная страница', name=username, data_product=data_product, bascet=bascet, username = session['username'])
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
        except:
            flash('Пользователь с таким адресом уже есть!', category='error')
        return redirect(url_for('index_autorization')) 
    return render_template('forma_registration.html', forma=forma, title='Регистрация')


@app.route('/autorization', methods=['POST', 'GET'])
def index_autorization():
    '''Обработка авторизации'''
    forma = FormAvt()
    if 'username'  in session:
        return redirect(url_for('index_shopping_basket', username=session['username']))
    if forma.validate_on_submit():
        datauser = Userprofile.query.filter_by(name=forma.name.data,psw=forma.psw.data).first()
        if datauser:
            session['mail'] = datauser.mail
            session['username'] = datauser.name
            session['name_id'] = datauser.id
            return redirect(url_for('index_shopping_basket', username=session['username']))
        else:
            flash('Неверное имя или пароль!', category='error')
    return render_template('forma_autorization.html', forma=forma, title='Авторизация')


@app.route('/basket/<username>', methods=['POST', 'GET'])
def index_shopping_basket(username):
    many = False
    card = False
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('index_autorization'))
    
    mail = session['mail']
    entries_product,user_card = get_data_product_bascet_and_card(session['name_id'],Bascet,Product,Usercard)
    if user_card:
        balance = user_card.balance
        card = True
    if user_card == None:
        balance = '-'
    if 'Exit' in request.form:
        return render_template('basket.html', name=username, mail=mail, data_product=entries_product, username=username, title='Корзина товаров', balance=balance, card=card)

    if 'productremove' in request.form:
        id_product = [i for i in request.form.values()]
        product_for_remove = Bascet.query.filter_by(user_id=int(session['name_id']),product_id=int(*id_product)).first()
        db.session.delete(product_for_remove)
        db.session.commit()
        return redirect(url_for('index_shopping_basket', username=session['username']))

    if 'makepurchase' in request.form:
        list_product,total_price = get_data_list_product_and_total_price([i.name for i in entries_product],[int(price) for price in request.form['makepurchase'].split()],[int(amount) for amount in request.form.getlist('amountproduct')])
        item = get_item([int(product[2]) for product in list_product])
        check_data = set_new_amount(item,entries_product)
        if balance - total_price > 0 and total_price != 0 and check_data != None:
            rm_bascet = Bascet.query.filter_by(user_id=int(session['name_id'])).all()
            [db.session.delete(rm) for rm in rm_bascet]
            user_card.balance -= total_price
            write_order = Orderuser(user_id=int(session['name_id']), list_product=list_product, order_price=total_price)
            db.session.add(write_order)
            db.session.commit()
        if balance - total_price < 0:
            user_card.balance = 1000
            db.session.commit()
            many = 'Не хватает денег!'
        return render_template('basket.html', name=username, mail=mail, data_product=entries_product,u=total_price, username=username, title='Корзина товаров', balance=balance, nomany=many,card=card)
        
    return render_template('basket.html', name=username, mail=mail, data_product=entries_product, username=username, title='Корзина товаров', balance=balance, card=card)


@app.route('/add-card/<username>', methods=['POST', 'GET'])
def index_card(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('index_autorization'))
    forma = FormAddCard()
    if forma.validate_on_submit():
        limit_entries = Usercard.query.filter_by(user_id=int(session['name_id'])).all()
        if len(limit_entries) > 0:
            return render_template('card_index.html', username=username, forma=forma, title='Привязка карты', yes='1') 
        number_card, validity, secret_code, surname, firstname, patronymic = [i for i in request.form.values()][1:-1]
        card = Usercard(user_id=int(session['name_id']), surname=surname, firstname=firstname, patronymic=patronymic, number_card=number_card, validity=validity, secret_code=secret_code, balance=add_balance())
        try:
            db.session.add(card)
            db.session.commit()
        except:
            flash('Неккоректное заполнение', category='error')
    return render_template('card_index.html', username=username, forma=forma, title='Привязка карты')


@app.errorhandler(404)
def pageNot(error):
    return redirect(url_for('index_autorization'))






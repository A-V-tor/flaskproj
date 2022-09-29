from flask_bootstrap import Bootstrap
from flask import render_template, request, url_for, redirect, flash, session, abort
from .forms import FormReg, FormAvt, FormAddCard
from flaskproj import app,db
from .models import Userprofile, Product, Bascet, Usercard, Orderuser
from .other import add_balance


Bootstrap(app)

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
        print(datauser)
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
    b = False
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('index_autorization'))
    else:
        mail = session['mail']
        personality = [i for i in Bascet.query.filter_by(user_id=session['name_id']).all()]
        data_product = [Product.query.filter_by(id=i.product_id).first() for i in personality]
        try:
            balance = Usercard.query.filter_by(user_id=int(session['name_id'])).first().balance
        except:
            balance = 0
        print('balance', balance)
        
        if 'Exit' in request.form:
            return render_template('basket.html', name=username, mail=mail, data_product=data_product, username=username, title='Корзина товаров', balance=balance)
        if 'productremove' in request.form:
            id_product = [i for i in request.form.values()]
            product_for_remove = Bascet.query.filter_by(user_id=int(session['name_id']),product_id=int(*id_product)).first()
            db.session.delete(product_for_remove)
            db.session.commit()
            return redirect(url_for('index_shopping_basket', username=session['username']))
        if 'makepurchase' in request.form:
            try:
                entries_for_order = zip([i.name for i in data_product],[i for i in request.form['makepurchase'].split()], [i for i in request.form.getlist('amountproduct')])
                list_product = [i for i in entries_for_order]
                data_order = zip([int(i) for i in request.form['makepurchase'].split()],[int(i) for i in request.form.getlist('amountproduct')])
                total_price  = sum([i[0]*i[1] for i in [i for i in data_order ]])
                if balance - total_price > 0 and total_price != 0:
                    record = Usercard.query.filter_by(user_id=int(session['name_id'])).first()
                    record.balance -= total_price
                    write_order = Orderuser(user_id=int(session['name_id']), list_product=list_product, order_price=total_price)
                    db.session.add(write_order)
                    db.session.commit()
                    
                else:
                    #record.balance = 1000
                    #db.session.commit()
                    print('hui')
                    b = 'Не хватает денег!'
            except:
                total_price = 'Ошибка'
            finally:
                return render_template('basket.html', name=username, mail=mail, data_product=data_product,u=total_price, username=username, title='Корзина товаров', balance=balance, nomany=b)
        return render_template('basket.html', name=username, mail=mail, data_product=data_product, username=username, title='Корзина товаров', balance=balance)


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






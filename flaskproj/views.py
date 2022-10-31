from datetime import datetime
from flask import abort, flash, redirect, render_template, request, session, url_for
from flask_bootstrap import Bootstrap
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from flaskproj import app, db

from .forms import FormAddCard, FormAvt, FormReg, New_Psw, PostUser
from .models import (
    Bascet,
    Orderuser,
    Product,
    TrendingProduct,
    Usercard,
    UserPosts,
    Userprofile,
)
from .other import (
    add_balance,
    get_back_product_item,
    get_data_list_product_and_total_price,
    get_data_product_bascet_and_card,
    get_item,
    get_next_product_item,
    set_new_amount,
    set_trend,
    get_data_list_for_index
)

Bootstrap(app)

login_manager = LoginManager(app)
login_manager.login_view = "index_autorization"
login_manager.login_message = " Нужно пройти процесс авторизации!"
login_manager.login_message_category = "error"


@login_manager.user_loader
def load_user(user):
    return Userprofile.query.get(user)


@app.route("/", methods=["POST", "GET"])
def index_main():
    """Обработка главной страницы"""
    data_product = Product.query.filter_by().order_by(Product.name).all()
    if current_user.is_authenticated:
        entries_bascet_user = Bascet.query.filter_by(user_id=current_user.id).all()
        lst = get_data_list_for_index(data_product, entries_bascet_user)
        if "product_name" in request.form:
            name_product = [i for i in request.form["product_name"]]
            bascet_write = Bascet(
                user_id=current_user.id, product_id=int(*name_product)
            )
            db.session.add(bascet_write)
            db.session.commit()
            return redirect(request.args.get("next") or url_for('index_main'))

        return render_template(
            "index.html",
            title="Главная страница",
            name=current_user.name,
            data_product=data_product,
            lst=lst
        )

    return render_template(
        "index.html", title="Главная страница", data_product=data_product
    )


@app.route("/description/<item>", methods=["POST", "GET"])
@login_required
def index_description(item):
    data_product = Product.query.filter_by(name=item).order_by(Product.name).first()
    all_product = Product.query.order_by(Product.name).all()
    next_item = get_next_product_item(all_product, data_product)
    back_item = get_back_product_item(all_product, data_product)
    name_product = data_product.id
    limit_entries = Bascet.query.filter_by(
        user_id=current_user.id, product_id=int(name_product)
    ).all()
    if len(limit_entries) > 0:
        return render_template(
            "description.html",
            title="Товар",
            data_product=data_product,
            next_item=next_item,
            back_item=back_item,
            limit=True,
        )

    if "productname" in request.form:
        bascet_write = Bascet(user_id=current_user.id, product_id=int(name_product))
        db.session.add(bascet_write)
        db.session.commit()
        return redirect(url_for("index_description", item=item))

    return render_template(
        "description.html",
        data_product=data_product,
        next_item=next_item,
        back_item=back_item,
        title="Товар",
    )


@app.route("/registration", methods=["POST", "GET"])
def index_registration():
    """Регистрация юзера"""
    forma = FormReg()

    if forma.validate_on_submit():
        try:
            user = Userprofile(
                mail=forma.email.data, name=forma.name.data, psw=forma.psw.data
            )
            db.session.add(user)
            db.session.commit()
            flash("Вы зарегестрированы, авторизуйтесь!", category="succes")
            return redirect(url_for("index_autorization"))
        except:
            flash("Пользователь с таким адресом уже существует!", category="error")
            return redirect(url_for("index_registration"))

    return render_template("forma_registration.html", forma=forma, title="Регистрация")


@app.route("/autorization", methods=["POST", "GET"])
def index_autorization():
    """Авторизация юзера"""
    forma = FormAvt()

    if forma.validate_on_submit():
        datauser = Userprofile.query.filter_by(
            name=forma.name.data, psw=forma.psw.data
        ).first()
        if datauser:
            login_user(datauser, remember=forma.remember.data)
            return redirect(
                request.args.get("next") or url_for("index_shopping_basket")
            )
        else:
            flash("Неверное имя или пароль!", category="error")

    return render_template("forma_autorization.html", forma=forma, title="Авторизация")


@app.route("/add-card", methods=["POST", "GET"])
@login_required
def index_card():
    card_user = False
    successfully_added = False
    forma = FormAddCard()
    limit_entries = Usercard.query.filter_by(user_id=current_user.id).all()

    if len(limit_entries) > 0:
        num = current_user.user_card[0].number_card
        return render_template(
            "card_index.html",
            forma=forma,
            title="Привязка карты",
            card_user=True,
            num=num,
        )

    if forma.validate_on_submit():
        number_card, validity, secret_code, surname, firstname, patronymic = [
            i for i in request.form.values()
        ][1:-1]
        if len(Usercard.query.filter_by(number_card=number_card).all()):
            return render_template(
                "card_index.html",
                limit_reached="Карта с данным номером уже добавлена!",
                forma=forma,
                title="Привязка карты",
                name=current_user.name,
            )
        card = Usercard(
            user_id=current_user.id,
            surname=surname,
            firstname=firstname,
            patronymic=patronymic,
            number_card=number_card,
            validity=validity,
            secret_code=secret_code,
            balance=add_balance(),
        )
        try:
            db.session.add(card)
            db.session.commit()
            successfully_added = True
        except:
            flash("Неккоректное заполнение", category="error")

    return render_template(
        "card_index.html",
        forma=forma,
        title="Платежнвя карта",
        name=current_user.name,
        successfully_added=successfully_added,
        card_user=card_user,
    )


@app.route("/out", methods=["POST", "GET"])
@login_required
def user_exit():
    logout_user()
    return redirect(url_for("index_autorization"))


@app.route("/rm", methods=["POST", "GET"])
@login_required
def remove_product():
    id_product = [i for i in request.form.values()]
    product_for_remove = Bascet.query.filter_by(
        user_id=current_user.id, product_id=int(*id_product)
    ).first()
    db.session.delete(product_for_remove)
    db.session.commit()
    return redirect(url_for("index_shopping_basket"))
    


@app.route("/rm-desc", methods=["POST", "GET"])
@login_required
def remove_product_for_description():
    id_product = [i for i in request.form.values()]
    product_for_remove = Bascet.query.filter_by(
        user_id=current_user.id, product_id=int(*id_product)
    ).first()
    db.session.delete(product_for_remove)
    db.session.commit()
    return redirect(
        url_for("index_description", item=Product.query.get(id_product).name)
    )


@app.route("/rm-main", methods=["POST", "GET"])
@login_required
def remove_product_for_main():
    id_product = [i for i in request.form.values()]
    product_for_remove = Bascet.query.filter_by(
        user_id=current_user.id, product_id=int(*id_product)
    ).first()
    db.session.delete(product_for_remove)
    db.session.commit()
    return redirect(request.args.get("next") or
        url_for("index_main")
    )


@app.route("/exit_in_bascet", methods=["POST", "GET"])
@login_required
def exit_in_bascet():
    return redirect(url_for("index_shopping_basket"))


@app.route("/order/<int:page>", methods=["POST", "GET"])
@login_required
def order_user(page=1):
    order_list = (
        Orderuser.query.filter_by(user_id=current_user.id)
        .order_by(Orderuser.date.desc())
        .paginate(page, 5, False)
    )
    return render_template(
        "orders.html", order_list=order_list, title="История заказов"
    )


@app.route("/password", methods=["POST", "GET"])
@login_required
def new_psw():
    forma = New_Psw()
    if forma.validate_on_submit():
        if request.form["new_psw"] == request.form["check_psw"]:
            Userprofile.query.filter_by(id=current_user.id).update(
                dict(psw=request.form["new_psw"])
            )
            db.session.commit()
            logout_user()
            return redirect(url_for("index_autorization"))
        else:
            flash("Пароли должны совпадать!", category="error")
    return render_template("new_psw.html", title="Смена пароля", forma=forma)


@app.route("/trend", methods=["POST", "GET"])
@login_required
def trend():
    trend_product = TrendingProduct.query.order_by(TrendingProduct.item.desc()).first()
    return render_template(
        "trend.html", trend=Product.query.get(trend_product.product_id)
    )


@app.route("/remove-card", methods=["POST", "GET"])
def card_remove():
    current_card = current_user.user_card[0]
    db.session.delete(current_card)
    db.session.commit()
    return redirect(url_for("index_card"))


@app.route("/post", methods=["POST", "GET"])
@login_required
def post_write():
    forma = PostUser()
    if forma.validate_on_submit():
        post = UserPosts(
            date=datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            title=request.form["title"],
            body=request.form["body"],
            user_name=current_user.name,
            user_id=current_user.id,
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("post_write"))
    return render_template("post.html", forma=forma)


@app.route('/search',methods=["POST","GET"])
def product_search():
    print(request.form["search"])
    data_for_find = request.form["search"]
    entries_search_product = Product.query.filter(Product.name.ilike(f'%{data_for_find}%')).all()
    return render_template('search.html',title='Результат поиска', data_product=entries_search_product)


@app.route('/bascet',methods=["POST","GET"])
@login_required
def index_shopping_basket():
    card = False
    order_number = False
    many = False
    balance = "карта не привязана"
    entries_product, user_card = get_data_product_bascet_and_card(
        current_user.id, Bascet, Product, Usercard
    )
    if user_card:
        balance = int(user_card.balance)
        card = True
    if "make_purchase" in request.form:
        list_product, total_price = get_data_list_product_and_total_price(
            [i.name for i in entries_product],
            [float(price) for price in request.form["make_purchase"].split()],
            [int(amount) for amount in request.form.getlist("amount_product")],
        )
        item = get_item([int(product[2]) for product in list_product])
        check_data, trend_list = set_new_amount(item, entries_product)
        if check_data is None and trend_list is None:
            return render_template(
                "bascet.html",
                name=current_user.name,
                mail=current_user.mail,
                data_product=entries_product, 
                total_price=total_price,
                title="Корзина товаров",
                balance=balance,
                card=card,
                order_number=order_number,
                many=many,
                no_amount=True,
            )

        if balance - total_price > 0 and total_price != 0:
            set_trend(TrendingProduct, trend_list)
            rm_bascet = Bascet.query.filter_by(user_id=current_user.id).all()
            [db.session.delete(rm) for rm in rm_bascet]
            [db.session.delete(rm) for rm in check_data]
            user_card.balance -= total_price
            new_order = Orderuser(
                user_id=current_user.id,
                date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), # ERROR d m Y
                list_product=list_product,
                order_price=total_price,
            )
            db.session.add(new_order)
            db.session.commit()
            order_number = (
                Orderuser.query.filter_by(user_id=current_user.id)
                .order_by(Orderuser.date)
                .all()[-1]
                .id
            ) # при обновлении окна с плывающем дивом отсылается повторный пост запрос, возможное решение написание шаблона для редиректа,order_number=order_number,total_price=total_price
            session['order_number'] = order_number
            session['total_price'] = total_price
            return redirect(url_for('pay_order'))

        if balance - total_price < 0:
            many = "Не хватает денег!"

        return render_template(
            "bascet.html",
            name=current_user.name,
            mail=current_user.mail,
            data_product=entries_product,
            total_price=total_price,
            title="Корзина товаров",
            balance=balance,
            card=card,
            order_number=order_number,
            many=many,
        )
    return render_template(
        "bascet.html",
        name=current_user.name,
        mail=current_user.mail,
        data_product=entries_product,
        title="Корзина товаров",
        balance=balance,
        card=card,
        many=many,
    )

# import requests
@app.route('/pay',methods=["POST","GET"])
@login_required
def pay_order():
    print(session['order_number'],session['total_price'])
    # return f"{requests.post('/pay', data = {'sum':session['total_price']})}"
    return render_template(
        'pay.html',
        order_number = session['order_number'],
        total_price = session['total_price'],
        )
    #return f"{session['order_number']},{session['total_price']}"
    # return redirect(url_for('https://demo.paykeeper.ru/create/'))

@app.errorhandler(404)
def pageNot(error):
    return redirect(url_for("index_autorization"))

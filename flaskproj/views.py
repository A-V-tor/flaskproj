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

from .forms import FormAddCard, FormAvt, FormReg
from .models import Bascet, Orderuser, Product, Usercard, Userprofile
from .other import (
    add_balance,
    get_data_list_product_and_total_price,
    get_data_product_bascet_and_card,
    get_item,
    set_new_amount,
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
    data_product = Product.query.filter_by().all()
    if current_user.is_authenticated:
        if request.method == "POST":
            name_product = [i for i in request.form.values()]
            limit_entries = Bascet.query.filter_by(
                user_id=current_user.id, product_id=int(*name_product)
            ).all()

            if len(limit_entries) > 0:
                return render_template(
                    "main.html",
                    title="Главная страница",
                    name=current_user.name,
                    data_product=data_product,
                )

            bascet_write = Bascet(
                user_id=current_user.id, product_id=int(*name_product)
            )
            db.session.add(bascet_write)
            db.session.commit()

        return render_template(
            "main.html",
            title="Главная страница",
            name=current_user.name,
            data_product=data_product,
        )

    return render_template(
        "main.html", title="Главная страница", data_product=data_product
    )


@app.route("/registration", methods=["POST", "GET"])
def index_registration():
    """Обработка регистрации"""
    forma = FormReg()

    if forma.validate_on_submit():
        try:
            user = Userprofile(
                mail=forma.email.data, name=forma.name.data, psw=forma.psw.data
            )
            db.session.add(user)
            db.session.commit()
        except:
            flash("Пользователь с таким адресом уже есть!", category="error")
        return redirect(url_for("index_autorization"))

    return render_template("forma_registration.html", forma=forma, title="Регистрация")


@app.route("/autorization", methods=["POST", "GET"])
def index_autorization():
    """Обработка авторизации"""
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


@app.route("/basket", methods=["POST", "GET"])
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
        balance = user_card.balance
        card = True

    if "make_purchase" in request.form:
        list_product, total_price = get_data_list_product_and_total_price(
            [i.name for i in entries_product],
            [int(price) for price in request.form["make_purchase"].split()],
            [int(amount) for amount in request.form.getlist("amount_product")],
        )
        item = get_item([int(product[2]) for product in list_product])
        check_data = set_new_amount(item, entries_product)

        if balance - total_price > 0 and total_price != 0 and check_data != None:
            rm_bascet = Bascet.query.filter_by(user_id=current_user.id).all()
            [db.session.delete(rm) for rm in rm_bascet]
            user_card.balance -= total_price
            write_order = Orderuser(
                user_id=current_user.id,
                list_product=list_product,
                order_price=total_price,
            )
            db.session.add(write_order)
            db.session.commit()
            order_number = (
                Orderuser.query.filter_by(user_id=current_user.id)
                .order_by(Orderuser.date)
                .all()[-1]
                .id
            )

        if balance - total_price < 0:
            user_card.balance = 1000
            db.session.commit()
            many = "Не хватает денег!"  # нигде не использую

        return render_template(
            "basket.html",
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
        "basket.html",
        name=current_user.name,
        mail=current_user.mail,
        data_product=entries_product,
        title="Корзина товаров",
        balance=balance,
        card=card,
        many=many,
    )


@app.route("/add-card", methods=["POST", "GET"])
@login_required
def index_card():
    successfully_added = False
    forma = FormAddCard()

    if forma.validate_on_submit():
        limit_entries = Usercard.query.filter_by(user_id=current_user.id).all()

        if len(limit_entries) > 0:
            return render_template(
                "card_index.html",
                forma=forma,
                title="Привязка карты",
                limit_reached="Данная карта уже существует!",
            )

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
        title="Привязка карты",
        name=current_user.name,
        successfully_added=successfully_added,
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


@app.route("/exit_in_bascet", methods=["POST", "GET"])
@login_required
def exit_in_bascet():
    return redirect(url_for("index_shopping_basket"))


@app.route("/test", methods=["POST", "GET"])
@login_required
def test():
    return render_template("test.html", name=current_user.name)


@app.errorhandler(404)
def pageNot(error):
    return redirect(url_for("index_autorization"))

import os
from datetime import datetime
from flask import flash, redirect, render_template, request, session, url_for
from flask_bootstrap import Bootstrap
from flask_mail import Message
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from flaskproj import app, db, mail, babel
#from flask_sqlalchemy import get_debug_queries   просмотр параметров запроса
from .forms import FormAvt, FormReg, New_Psw, PostUser
from .models import (
    Bascet,
    Orderuser,
    Product,
    TrendingProduct,
    UserPosts,
    Userprofile,
)
from .other import (
    get_data_list_product_and_total_price,
    get_data_product_bascet,
    get_item,
    set_new_amount,
    set_trend,
    get_list_of_actions,
    create_payment,
    check_status,
    generate_confirmation_token,
    confirm_token,
)

Bootstrap(app)

login_manager = LoginManager(app)
login_manager.login_view = "index_autorization"
login_manager.login_message = " Нужно пройти процесс авторизации!"
login_manager.login_message_category = "error"


@login_manager.user_loader
def load_user(user):
    return Userprofile.query.get(user)


@babel.localeselector
def get_locale():
    if request.args.get("lang"):
        session["lang"] = request.args.get("lang")
    return session.get("lang", "ru")


@app.route("/", methods=["POST", "GET"])
def index_main():
    """Обработка главной страницы"""
    data_product = Product.query.filter_by().order_by(Product.name).all()
    if current_user.is_authenticated:
        entries_bascet_user = Bascet.query.filter_by(user_id=current_user.id).all()
        lst = get_list_of_actions(data_product, entries_bascet_user)
        if "product_name" in request.form:
            name_product = [request.form["product_name"]]
            bascet_write = Bascet(
                user_id=current_user.id, product_id=int(*name_product)
            )
            db.session.add(bascet_write)
            db.session.commit()
            return redirect(request.args.get("next") or url_for("index_main"))

        return render_template(
            "index.html",
            title="Главная страница",
            name=current_user.name,
            data_product=data_product,
            lst=lst,
        )

    return render_template(
        "index.html", title="Главная страница", data_product=data_product
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
            token = generate_confirmation_token(user.mail)
            confirm_url = url_for("confirm_email", token=token, _external=True)
            html = render_template("activ.html", confirm_url=confirm_url)
            msg = Message(
                "Подтверждение регистрации", recipients=[os.getenv("test_mail")]
            )
            msg.html = html
            mail.send(msg)
            flash("Вы зарегестрированы, проверьте почту!", category="succes")
            return redirect(url_for("index_autorization"))
        except:
            flash("Пользователь с таким адресом уже существует!", category="error")
            return redirect(url_for("index_registration"))

    return render_template("forma_registration.html", forma=forma, title="Регистрация")


@app.route("/confirm/<token>", methods=["POST", "GET"])
def confirm_email(token):
    """Подтверждение почтового ящика"""
    try:
        mail = confirm_token(token)
    except:
        flash(
            "Ссылка для подтверждения недействительна или срок ее действия истек.",
            category="error",
        )
        return redirect(url_for("index_registration"))
    user = Userprofile.query.filter_by(mail=mail).first_or_404()
    if user.confirmed:
        flash("Аккаунт уже подтвержден. Пожалуйста, войдите.", category="succes")
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash("Аккаунт подтвержден!", category="succes")
    return redirect(url_for("index_autorization"))


@app.route("/description/<int:page>", methods=["POST", "GET"])
@login_required
def index_description(page):
    session["page"] = page
    product = Product.query.filter_by().order_by(Product.name).paginate(page, 1, False)
    [item] = [i.id for i in product.items]
    print(item)
    limit_entries = Bascet.query.filter_by(
        user_id=current_user.id, product_id=item
    ).all()
    # print(get_debug_queries())
    if len(limit_entries) > 0:
        return render_template(
            "description.html",
            pr=product,
            title="Товар",
            limit=True,
        )

    if "productname" in request.form:
        product_id = request.form.get("productname")
        bascet_write = Bascet(user_id=current_user.id, product_id=product_id)
        db.session.add(bascet_write)
        db.session.commit()
        return redirect(url_for("index_description", page=page))

    return render_template(
        "description.html",
        pr=product,
        title="Товар",
    )


@app.route("/autorization", methods=["POST", "GET"])
def index_autorization():
    """Авторизация юзера"""
    forma = FormAvt()

    if forma.validate_on_submit():
        datauser = Userprofile.query.filter_by(
            mail=forma.email.data, psw=forma.psw.data
        ).first()
        if datauser:
            login_user(datauser, remember=forma.remember.data)
            return redirect(
                request.args.get("next") or url_for("index_shopping_basket")
            )
        else:
            flash("Неверный адрес или пароль!", category="error")

    return render_template("forma_autorization.html", forma=forma, title="Авторизация")


@app.route("/out", methods=["POST", "GET"])
@login_required
def user_exit():
    logout_user()
    return redirect(url_for("index_autorization"))


@app.route("/remove", methods=["POST", "GET"])
@login_required
def remove_product_for_main():
    try:
        id_product = [i for i in request.form.values()]
        product_for_remove = Bascet.query.filter_by(
            user_id=current_user.id, product_id=int(*id_product)
        ).first()
        db.session.delete(product_for_remove)
        db.session.commit()
    except:
        pass
    finally:
        if "product_remove" in request.form:
            return redirect(request.args.get("next") or url_for("index_main"))
        elif "product_remove_for_description" in request.form:
            return redirect(url_for("index_description", page=session["page"]))
        elif "productname" in request.form:
            return redirect(url_for("product_search"))
        return redirect(url_for("index_shopping_basket"))


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
    trend_product = db.session.execute(
        db.select(TrendingProduct).order_by(TrendingProduct.item.desc())
    ).scalar()
    product = db.session.execute(
        db.select(Product).filter_by(id=trend_product.product_id)
    ).scalar()
    return render_template("trend.html", trend=product)


@app.route("/post", methods=["POST", "GET"])
@login_required
def post_write():
    forma = PostUser()
    if forma.validate_on_submit():
        post = UserPosts(
            date=datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            title=request.form["title"],
            body=request.form.get("body"),
            user_name=current_user.name,
            user_id=current_user.id,
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("post_write"))
    return render_template("post.html", forma=forma)


@app.route("/search", methods=["POST", "GET"])
@login_required
def product_search():
    """
    Слово записывается в словарь сессий

    при первом проходе функции. Формируются именованные

    кортежи для добавления, удаления.

    """
    try:
        session["search"] = request.form["search"]
    except:
        pass
    if "productname" in request.form:
        product_id = request.form.get("productname")
        db.session.add(Bascet(user_id=current_user.id, product_id=product_id))
        db.session.commit()
        return redirect(url_for(request.args.get("next") or "product_search"))
    entries_search_product = db.session.execute(
        db.select(Product).filter(Product.name.ilike(f'%{session["search"]}%'))
    ).scalars()
    entries_bascet_user = Bascet.query.filter_by(user_id=current_user.id).all()
    list_data_products = [i for i in entries_search_product]
    lst = get_list_of_actions(list_data_products, entries_bascet_user)
    return render_template("search.html", title="Результат поиска", data_product=lst)


@app.route("/bascet", methods=["POST", "GET"])
@login_required
def index_shopping_basket():
    order_number = False
    entries_product = get_data_product_bascet(current_user.id, Bascet, Product)
    if "make_purchase" in request.form:
        list_product, total_price = get_data_list_product_and_total_price(
            [i.name for i in entries_product],
            [float(price) for price in request.form["make_purchase"].split()],
            [int(amount) for amount in request.form.getlist("amount_product")],
        )
        current_amount = get_item([int(product[2]) for product in list_product])
        # переделать для сети чтобы изменение кол-ва происходила после успешной оплаты
        check_data, trend_list = set_new_amount(current_amount, entries_product)
        if check_data is None and trend_list is None:
            return render_template(
                "bascet.html",
                name=current_user.name,
                mail=current_user.mail,
                data_product=entries_product,
                total_price=total_price,
                title="Корзина товаров",
                order_number=order_number,
                no_amount=True,
            )

        set_trend(TrendingProduct, trend_list)
        rm_bascet = Bascet.query.filter_by(user_id=current_user.id).all()
        [db.session.delete(rm) for rm in rm_bascet]
        [db.session.delete(rm) for rm in check_data]
        new_order = Orderuser(
            user_id=current_user.id,
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # ERROR d m Y
            list_product=list_product,
            order_price=total_price,
        )
        db.session.add(new_order)
        order_number = (
            Orderuser.query.filter_by(user_id=current_user.id)
            .order_by(Orderuser.date)
            .all()[-1]
        )
        resp = create_payment(order_number, total_price)
        db.session.commit()
        return redirect(resp)

    return render_template(
        "bascet.html",
        name=current_user.name,
        mail=current_user.mail,
        data_product=entries_product,
        title="Корзина товаров",
    )


@app.route("/status-pay/<id>", methods=["POST", "GET"])
@login_required
def status_pay(id):
    # https://demo.paykeeper.ru/payments/settings
    pay = False
    order = db.session.execute(
        db.select(Orderuser).filter_by(user_id=current_user.id, invoice_id=id)
    ).scalar()
    print(order)
    if check_status(order) == "paid":
        pay = "Оплачен"
    return render_template("status_pay.html", pay=pay, id=id)


@app.route("/about", methods=["POST", "GET"])
def about():
    return render_template("about.html")


# @app.errorhandler(404)
# def pageNot(error):
#     return redirect(url_for("index_autorization"))

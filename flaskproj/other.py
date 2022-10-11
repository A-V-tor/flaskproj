import random

from flaskproj import db


def add_balance():
    """Генерация едениц оплаты для карты пользователя"""
    a = random.randint(10, 100)
    b = random.randint(0, 15)
    c = random.choice([1.5, 2.5, 3.5])
    res = a + b + c
    return res


def get_item(item):
    for i in item:
        yield i


def get_data_product_bascet_and_card(item, bascet, product, usercard):
    """
    Выбирается запись корзины для текущего юзера, затем

    создается список с записями товаров корзины. В user_card

    хранится карта оплаты.
    """
    res = [i for i in bascet.query.filter_by(user_id=item).all()]
    entries_product = [product.query.filter_by(id=i.product_id).first() for i in res]
    user_card = usercard.query.filter_by(user_id=item).first()
    return entries_product, user_card


def get_data_list_product_and_total_price(name_product, price, amount):
    """
    Получение кортежа данных имени, цены и количества товара

    для записи в модель заказа и итоговой суммы для списания с карты.
    """
    zip_data = zip(name_product, price, amount)
    list_product_data = [i for i in zip_data]
    data_for_order = zip(price, amount)
    total_price = sum([i[0] * i[1] for i in [i for i in data_for_order]])
    return list_product_data, total_price


def set_new_amount(item, entries_product):
    """
    Запись в БД нового значения  кол-ва товара
    и возврат списка записей о нулевом остатке.
    """
    new_amount = [value.amount - next(item) for value in entries_product]
    rm_list = []
    trend_list = []
    for product in [value for value in entries_product]:
        if new_amount[0] > 0:
            trend_list.append([product.id, product.amount - new_amount[0]])
            product.amount = new_amount[0]
            new_amount = new_amount[1:]
        elif new_amount[0] == 0:
            trend_list.append([product.id, product.amount - new_amount[0]])
            rm_list.append(product)
        else:
            return None, None
    return rm_list, trend_list


def set_trend(trending_product, trend_list):
    for i in trend_list:
        check_data_product = trending_product.query.filter_by(product_id=i[0]).first()
        if check_data_product == None:
            db.session.add(trending_product(product_id=i[0], item=i[1]))
        else:
            item_new = check_data_product.item + i[1]
            trending_product.query.filter_by(product_id=i[0]).update(
                dict(item=item_new)
            )
        db.session.commit()


def get_next_product_item(lst, current_item):
    for n, i in enumerate(lst):
        if i == current_item:
            try:
                return lst[n + 1]
            except:
                return lst[0]


def get_back_product_item(lst, current_item):
    for n, i in enumerate(lst):
        if i == current_item:
            try:
                return lst[n - 1]
            except:
                return lst[-1]

from itsdangerous import URLSafeTimedSerializer
import os
from collections import namedtuple
import json
import random

from flaskproj import db
# https://demo.paykeeper.ru/payments/invoices
# https://docs.paykeeper.ru/metody-integratsii/poluchenie-pryamoj-ssylki-na-oplatu/

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


def get_data_product_bascet(item, bascet, product):
    """
    Выбирается запись корзины для текущего юзера, затем

    создается список с записями товаров корзины.
    """
    res = [i for i in bascet.query.filter_by(user_id=item).all()]
    entries_product = [product.query.filter_by(id=i.product_id).first() for i in res]
    return entries_product 


def get_data_list_product_and_total_price(name_product, price, amount):
    """
    Получение кортежа данных имени, цены и количества товара

    для записи в модель заказа и итоговой суммы для списания с карты.
    """
    zip_data = zip(name_product, price, amount)
    list_product_data = [i for i in zip_data]
    data_for_total_price= zip(price, amount)
    total_price = sum([i[0] * i[1] for i in [i for i in data_for_total_price]])
    return list_product_data, total_price


def set_new_amount(item, entries_product):
    """
    Запись в БД нового значения  кол-ва товара
    и возврат списка записей о нулевом остатке.
    """
    new_amount = [current.amount - next(item) for current in entries_product]
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

def get_data_list_for_index(data_product, entries_bascet_user):
    """
    Формирование списка с именными кортежами обозначающие продукты

    находящиеся и отсутствующие в корзине.
    """
    lst = []
    rm_item = namedtuple('item', 'rm')
    add_item = namedtuple('item', 'add')
    for i in data_product:
        if i.id in [i.product_id for i in entries_bascet_user]:
            lst.append(rm_item(i))
        else:
            lst.append(add_item(i))
    return lst

import base64
import requests


pay_login = 'demo'
pay_password = 'demo'
pay_domain = 'http://demo.paykeeper.ru'

            
def get_encoding_logpass(): 
    logpass_for_decoding = f'{pay_login}:{pay_password}'
    logpass__bytes = logpass_for_decoding.encode('ascii')
    base64_bytes = base64.b64encode(logpass__bytes)
    base64_logpass = base64_bytes.decode('ascii')
    print('base64_logpass',base64_logpass)
    return base64_logpass

HEADERS = {
    'content-type': 'application/x-www-form-urlencoded',
    'authorization': f'Basic {get_encoding_logpass()}',
}

def create_payment(order, cost):
    # получаем токен из paykeeper
    url = f'{pay_domain}/info/settings/token/'
    sess = requests.Session()
    response = sess.get(url, headers=HEADERS)
    print('response',response.text)
    try:
        response_json = response.json()
    except Exception:
        return None

    if response_json:
        token = response_json.get('token')
        print('token',token)
        # при наличии токена создаем заказ и отправляем для формирования ссылки на оплату
        if token:
            url = f'{pay_domain}/change/invoice/preview/'
            payload = {
                'pay_amount': cost,
                'orderid': order.id,
                'token': token
            }
            response = sess.post(url, data=payload, headers=HEADERS, allow_redirects=True)
            try:
                response_json = response.json()
            except Exception:
                return None

            invoice_id = response_json.get('invoice_id')
            order.invoice_id = str(invoice_id)
            # возвращаем ссылку на оплату
            return f'{pay_domain}/bill/{invoice_id}/'
    return None


def check_status(order):
    ''' Проверка статуса оплаты заказа '''

    url = f'{pay_domain}/info/invoice/byid/?id={order.invoice_id}'
    response = requests.request('GET', url, headers=HEADERS)

    # получаем статус платежа
    response_json = response.json()
    status = response_json.get('status')
    return status


def generate_confirmation_token(email):
    ''' Генерация токена подтверждения '''
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'), salt="activate")
    return serializer.dumps(email)


def confirm_token(token, expiration=3600):
    '''Чтение токена, токен действителен на протяжении часа'''
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
    try:
        email = serializer.loads(
            token,
            salt="activate",
            max_age=expiration
        )
    except:
        return False
    return email


import random


def add_balance():
    '''Генерация едениц оплаты для карты пользователя'''
    a = random.randint(10, 100)
    b = random.randint(0, 15)
    c = random.choice([1.5, 2.5, 3.5])
    res = a + b + c
    return res


#print(add_balance())
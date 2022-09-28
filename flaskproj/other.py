import random
from re import A


def add_balance():
    a = random.randint(10, 100)
    b = random.randint(0, 15)
    c = random.choice([1.5, 2.5, 3.5])
    res = a + b + c
    return res


#print(add_balance())
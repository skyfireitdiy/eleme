from pony.orm import *
from flask_login import UserMixin

from config import config

db = Database()


class User(db.Entity, UserMixin):
    id = PrimaryKey(int, auto=True)
    nickname = Required(str, unique=True)
    name = Required(str)
    password = Required(str)
    phone = Required(str)
    address = Optional(str)
    role = Required(int)
    restaurant = Set("Restaurant")
    order = Set("Order")


class Restaurant(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    address = Required(str)
    owner = Required(User)
    disable = Required(bool, default=False)
    food = Set("Food")
    oder = Set("Order")


class Food(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    price = Required(float)
    disable = Required(bool, default=False)
    restaurant = Required(Restaurant)
    order_detail = Set("OrderDetail")


class Order(db.Entity):
    id = PrimaryKey(int, auto=True)
    total = Required(float)
    restaurant = Optional(Restaurant)
    custom = Required(User)
    status = Required(int)
    order_detail = Set("OrderDetail")


class OrderDetail(db.Entity):
    order_id = Required(Order)
    food = Required(Food)
    count = Required(int)


database_config = config["database"]

db.bind(provider=database_config["provider"],
        host=database_config["host"],
        port=database_config["port"],
        user=database_config["user"],
        passwd=database_config["passwd"],
        db=database_config["db"])

db.generate_mapping(create_tables=True)

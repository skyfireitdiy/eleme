"""
数据库管理
"""
from pony.orm import *
from flask_login import UserMixin

from config import config
from datetime import datetime

db = Database()


class User(db.Entity, UserMixin):
    """
    用户表
    """
    id = PrimaryKey(int, auto=True)
    nickname = Required(str, unique=True)
    name = Required(str)
    password = Required(str)
    phone = Required(str)
    address = Optional(str)
    role = Required(int)
    restaurant = Set("Restaurant")
    custom = Set("Order", reverse="custom")
    courier = Set("Order", reverse="courier")


class Restaurant(db.Entity):
    """
    餐馆表
    """
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    address = Required(str)
    owner = Required(User)
    disable = Required(bool, default=False)
    food = Set("Food")
    order = Set("Order")


class Food(db.Entity):
    """
    菜单表
    """
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    price = Required(float)
    disable = Required(bool, default=False)
    restaurant = Required(Restaurant)
    order_detail = Set("OrderDetail")


class Order(db.Entity):
    """
    订单表
    """
    serial_number = PrimaryKey(str)
    time = Required(datetime)
    total = Required(float)
    restaurant = Required(Restaurant)
    custom = Required(User)
    courier = Optional(User)
    # 0 下单 1 接受 2 拒绝 3 取消 4 指定派单员 5 完成
    status = Required(int, default=0)
    order_detail = Set("OrderDetail")


class OrderDetail(db.Entity):
    """
    订单详情表
    """
    order = Required(Order)
    food = Required(Food)


# 加载数据库配置并创建数据表（如果不存在）
database_config = config["database"]

db.bind(provider=database_config["provider"],
        host=database_config["host"],
        port=database_config["port"],
        user=database_config["user"],
        passwd=database_config["passwd"],
        db=database_config["db"])

db.generate_mapping(create_tables=True)

"""
订单管理
"""
import datetime
import random
import string

from flask import *
from flask_login import current_user, login_required
from pony.orm import *

from database import Order, OrderDetail, Restaurant, User, Food, db
from user import merchant_required

order_blueprints = Blueprint("order", "order", static_folder="static", template_folder="template",
                             url_prefix="/order", static_url_path="/static")


@order_blueprints.route("/get", methods=["GET"])
@db_session
@login_required
def get():
    """
    显示订单，不同用户角色显示的不同
    """
    couriers = select(r for r in User if r.role == 2)[:]
    if current_user.role == 0:
        order_info = select(o for o in Order
                            for r in Restaurant
                            if r.owner == current_user and o.restaurant == r)[:]
    elif current_user.role == 1:
        order_info = select(o for o in Order
                            if o.custom == current_user)[:]
    else:
        order_info = select(o for o in Order
                            if o.courier == current_user)[:]
    return render_template("order_get.html", order_info=order_info, user=current_user, couriers=couriers)


@order_blueprints.route("/detail", methods=["GET"])
@db_session
@login_required
def detail():
    """
    订单详情
    """
    id = request.args.get("id", None)
    return render_template("order_detail.html", details=select(r for r in OrderDetail if r.order.serial_number == id))


@order_blueprints.route("/add", methods=["POST"])
@login_required
@db_session
def add():
    """
    创建订单，由客户提交选中的菜品
    """
    food_ids = request.form.getlist("foods")
    restaurant_id = request.form.get("restaurant", None)
    total = 0
    time = datetime.datetime.now()
    serial_number = time.strftime("%Y%m%d%H%M%S") + ''.join([random.choice(string.digits) for i in range(10)])
    restaurant = select(r for r in Restaurant if r.id == int(restaurant_id)).first()
    custom = select(r for r in User if r.id == current_user.id).first()
    for i in food_ids:
        f = select(r for r in Food if r.id == int(i)).first()
        total += f.price
    order = Order(
        serial_number=serial_number,
        time=time,
        total=total,
        restaurant=restaurant,
        custom=custom
    )
    for i in food_ids:
        OrderDetail(
            order=order,
            food=i
        )
    db.commit()
    flash("Ordering success")
    return redirect(url_for("food.list_food") + "?id=" + restaurant_id)


@order_blueprints.route("/set_status", methods=["GET"])
@login_required
@db_session
def set_status():
    """
    修改订单状态
    """
    status = int(request.args.get("status", None))
    id = request.args.get("id", None)
    order = Order.get(serial_number=id)
    if order is None:
        flash("Parameter error", "error")
    else:
        order.status = status
        db.commit()
    return redirect(url_for("order.get"))


@order_blueprints.route("/set_courier", methods=["POST"])
@merchant_required
@db_session
def set_courier():
    """
    指定派单员，同时会把订单状态修改为正在派送
    """
    serial_number = request.form.get("serial_number", None)
    courier_id = int(request.form.get("courier", None))
    courier = User.get(id=courier_id, role=2)
    order = select(r for r in Order if r.serial_number == serial_number).first()
    order.status = 4
    order.courier = courier
    db.commit()
    return redirect(url_for("order.get"))

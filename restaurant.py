"""
餐馆管理
"""
from flask import *
from flask_login import current_user
from flask_wtf import FlaskForm
from pony.orm import *
from wtforms import StringField
from wtforms.validators import *

from database import Restaurant, db
from user import merchant_required, custom_required

restaurant_blueprints = Blueprint("restaurant", "restaurant", static_folder="static", template_folder="template",
                                  url_prefix="/restaurant", static_url_path="/static")


@restaurant_blueprints.route("/manage", methods=["GET"])
@db_session
@merchant_required
def manage():
    """
    餐馆管理，显示餐馆列表，并且可以删除、添加
    """
    return render_template("restaurant_manage.html",
                           restaurants=select(r for r in Restaurant if r.owner == current_user and not r.disable)[:])


@restaurant_blueprints.route("/list_restaurant", methods=["GET"])
@db_session
@custom_required
def list_restaurant():
    """
    点餐的餐馆界面
    """
    return render_template("list_restaurant.html",
                           restaurants=select(r for r in Restaurant if not r.disable)[:])


class AddRestaurantForm(FlaskForm):
    """
    添加餐馆的表单
    """
    name = StringField("Name", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])


@restaurant_blueprints.route("add", methods=["GET", "POST"])
@db_session
@merchant_required
def add():
    """
    添加餐馆
    """
    form = AddRestaurantForm()
    if form.validate_on_submit():
        Restaurant(name=form.name.data,
                   address=form.address.data,
                   owner=current_user)
        db.commit()
        flash("Added successfully")
        return redirect(url_for("restaurant.manage"))
    return render_template("restaurant_add.html", form=form)


@restaurant_blueprints.route("delete", methods=["GET"])
@db_session
@merchant_required
def delete():
    """
    删除餐馆
    :return:
    """
    id = request.args.get("id", None)
    if id is None:
        flash("Parameter error", "error")
        return redirect(url_for("restaurant.manage"))
    res = select(r for r in Restaurant if r.id == id and not r.disable).first()
    if res is None:
        flash("This restaurant does not exist or has been deleted", "error")
        return redirect(url_for("restaurant.manage"))
    res.disable = True
    flash("Successfully deleted")
    return redirect(url_for("restaurant.manage"))

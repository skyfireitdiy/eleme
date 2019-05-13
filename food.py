"""
菜单管理
"""
from database import Food, db, Restaurant
from pony.orm import *
from flask import *
from user import merchant_required, custom_required
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField
from wtforms.validators import *

food_blueprints = Blueprint("food", "food", static_folder="static", template_folder="template",
                            url_prefix="/food", static_url_path="/static")


class AddFoodForm(FlaskForm):
    """
    添加菜单的表单
    """
    name = StringField("Name", validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired()])
    restaurant = IntegerField("Restaurant", validators=[DataRequired()])
    submit = SubmitField("Add")


@food_blueprints.route("/manage", methods=["GET"])
@db_session
@merchant_required
def manage():
    """
    菜单管理，get请求，需要带餐馆id，返回该餐馆下的菜单
    :return: 菜单页面
    """
    id = request.args.get("id", None)
    if id is None:
        flash("Parameter error", "error")
        return redirect(url_for("restaurant.manage"))
    return render_template("food_manage.html",
                           foods=select(r for r in Food if r.restaurant.id == id and not r.disable)[:],
                           restaurant_id=id)


@food_blueprints.route("/add", methods=["GET", "POST"])
@db_session
@merchant_required
def add():
    """
    添加菜品
    """
    form = AddFoodForm()
    if form.validate_on_submit():
        res = select(r for r in Restaurant if r.id == int(form.restaurant.data)).first()
        if res is None:
            flash("Parameter error", "error")
            return redirect(url_for("restaurant.manage"))
        Food(
            name=form.name.data,
            price=form.price.data,
            restaurant=res
        )
        db.commit()
        flash("Added successfully")
        return redirect(url_for("food.manage") + "?id=" + str(form.restaurant.data))
    id = request.args.get("id", None)
    if id is None:
        flash("Parameter error", "error")
        return redirect(url_for("restaurant.manage"))
    return render_template("food_add.html", form=form, restaurant_id=id)


@food_blueprints.route("/delete", methods=["GET"])
@db_session
@merchant_required
def delete():
    """
    删除菜品，软删除，因为在订单中会有改菜品的记录，受外键约束，不能直接删除
    """
    id = request.args.get("id", None)
    res = request.args.get("res", None)
    if id is None or res is None:
        flash("Parameter error", "error")
        return redirect(url_for("restaurant.manage"))
    food = select(r for r in Food if r.id == id and not r.disable).first()
    if food is None:
        flash("This dish does not exist or has been deleted", "error")
        return redirect(url_for("restaurant.manage"))
    food.disable = True
    db.commit()
    flash("Successfully deleted")
    return redirect(url_for("food.manage") + "?id=" + res)


@food_blueprints.route("/list_food", methods=["GET"])
@db_session
@custom_required
def list_food():
    """
    点餐页面
    """
    id = request.args.get("id", None)
    return render_template("list_food.html", foods=select(f for f in Food
                                                          for r in Restaurant
                                                          if f.restaurant == r and
                                                          r.id == int(id)
                                                          ), restaurant=id)

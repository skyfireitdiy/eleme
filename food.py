from database import Food, db, Restaurant
from pony.orm import *
from flask import *
from user import merchant_required
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField
from wtforms.validators import *

food_blueprints = Blueprint("food", "food", static_folder="static", template_folder="template",
                            url_prefix="/food")


class AddFoodForm(FlaskForm):
    name = StringField("名称", validators=[DataRequired()])
    price = FloatField("单价", validators=[DataRequired()])
    restaurant = IntegerField("餐馆", validators=[DataRequired()])
    submit = SubmitField("添加")


@food_blueprints.route("/manage", methods=["GET"])
@db_session
@merchant_required
def manage():
    id = request.args.get("id", None)
    if id is None:
        flash("参数错误")
        return redirect(url_for("restaurant.manage"))
    return render_template("food_manage.html",
                           foods=select(r for r in Food if r.restaurant.id == id and not r.disable)[:],
                           restaurant_id=id)


@food_blueprints.route("/add", methods=["GET", "POST"])
@db_session
@merchant_required
def add():
    form = AddFoodForm()
    if form.validate_on_submit():
        res = select(r for r in Restaurant if r.id == int(form.restaurant.data)).first()
        if res is None:
            flash("参数错误")
            return redirect(url_for("restaurant.manage"))
        Food(
            name=form.name.data,
            price=form.price.data,
            restaurant=res
        )
        db.commit()
        flash("添加成功")
        return redirect(url_for("food.manage") + "?id=" + str(form.restaurant.data))
    id = request.args.get("id", None)
    if id is None:
        flash("参数错误")
        return redirect(url_for("restaurant.manage"))
    return render_template("food_add.html", form=form, restaurant_id=id)


@food_blueprints.route("/delete", methods=["GET"])
@db_session
@merchant_required
def delete():
    id = request.args.get("id", None)
    res = request.args.get("res", None)
    if id is None or res is None:
        flash("参数错误")
        return redirect(url_for("restaurant.manage"))
    food = select(r for r in Food if r.id == id and not r.disable).first()
    if food is None:
        flash("不存在此菜品或已被删除")
        return redirect(url_for("restaurant.manage"))
    food.disable = True
    db.commit()
    flash("删除成功")
    return redirect(url_for("food.manage") + "?id=" + res)
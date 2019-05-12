from database import Restaurant, db
from pony.orm import *
from user import merchant_required
from flask_login import current_user
from flask import *
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import *

restaurant_blueprints = Blueprint("restaurant", "restaurant", static_folder="static", template_folder="template",
                                  url_prefix="/restaurant")


@restaurant_blueprints.route("/manage", methods=["GET"])
@db_session
@merchant_required
def manage():
    return render_template("restaurant_manage.html",
                           restaurants=select(r for r in Restaurant if r.owner == current_user and not r.disable)[:])


class AddRestaurantForm(FlaskForm):
    name = StringField("名称", validators=[DataRequired()])
    address = StringField("地址", validators=[DataRequired()])
    submit = SubmitField("添加", validators=[DataRequired()])


@restaurant_blueprints.route("add", methods=["GET", "POST"])
@db_session
@merchant_required
def add():
    form = AddRestaurantForm()
    if form.validate_on_submit():
        Restaurant(name=form.name.data,
                   address=form.address.data,
                   owner=current_user)
        db.commit()
        flash("添加成功")
        return redirect(url_for("restaurant.manage"))
    return render_template("restaurant_add.html", form=form)


@restaurant_blueprints.route("delete", methods=["GET"])
@db_session
@merchant_required
def delete():
    id = request.args.get("id", None)
    if id is None:
        flash("参数错误")
        return redirect(url_for("restaurant.manage"))
    res = select(r for r in Restaurant if r.id == id and not r.disable).first()
    if res is None:
        flash("不存在此餐馆或已被删除")
        return redirect(url_for("restaurant.manage"))
    res.disable = True
    flash("删除成功")
    return redirect(url_for("restaurant.manage"))

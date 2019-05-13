"""
用户管理
"""

import flask_login

from functools import wraps
from flask_login import current_user
from flask import *
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import *
from database import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from pony.orm import *

user_blueprints = blueprints.Blueprint("user", "user", static_folder="static", template_folder="template",
                                       url_prefix="/user", static_url_path="/static")


def merchant_required(func):
    """
    判断用户是否是商家的包装器，如果不是，就跳转到登录界面
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in flask_login.config.EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not flask_login.current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif flask_login.current_user.role != 0:
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)

    return decorated_view


def custom_required(func):
    """
    判断用户是否是客户的包装器，如果不是，就跳转到登录界面
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in flask_login.config.EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not flask_login.current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif flask_login.current_user.role != 1:
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)

    return decorated_view


def delivery_required(func):
    """
    判断用户是否是派单员的包装器，如果不是，就跳转到登录界面
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in flask_login.config.EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not flask_login.current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif flask_login.current_user.role != 2:
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)

    return decorated_view


@db_session
def get_user(user_id):
    """
    获取用户对象
    :param user_id: 用户id
    :return: 用户对象
    """
    return select(r for r in User if r.id == user_id).first()


class LoginForm(FlaskForm):
    """
    登录表单
    """
    nickname = StringField("Nickname", validators=[DataRequired()], default="")
    password = PasswordField("Password", validators=[DataRequired()], default="")
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    """
    注册表单
    """
    nickname = StringField("Nickname", validators=[DataRequired(), Length(1, 20)], default="")
    name = StringField("Name", validators=[DataRequired(), Length(1, 20)], default="")
    password1 = PasswordField("Password", validators=[DataRequired(), Length(8, 16)], default="")
    password2 = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password1")], default="")
    phone = StringField("Phone", validators=[DataRequired(), Regexp(r"\d{6,13}", 0)], default="")
    address = StringField("Address", validators=[DataRequired()], default="")
    role = SelectField("Role", choices=[('0', "Merchant"), ('1', "Customer"), ('2', "Delivery staff")])


@user_blueprints.route("/register", methods=["GET", "POST"])
@db_session
def register():
    """
    用户注册
    """
    form = RegisterForm()
    if form.validate_on_submit():
        if select(r for r in User if r.nickname == form.nickname.data).first() is not None:
            form.nickname.errors.append('User "%s" already exist' % form.nickname.data)
            return render_template('register.html', form=form)
        User(
            nickname=form.nickname.data,
            name=form.name.data,
            password=generate_password_hash(form.password1.data),
            phone=form.phone.data,
            address=form.address.data,
            role=int(form.role.data))
        db.commit()
        flash('User "%s" registration is successful, Please login' % form.nickname.data)
        return redirect(url_for("user.login"))
    return render_template('register.html', form=form)


@user_blueprints.route("/login", methods=["GET", "POST"])
@db_session
def login():
    """
    用户登录
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = select(r for r in User if r.nickname == form.nickname.data).first()
        if user is None:
            form.nickname.errors.append("User does not exist")
            return render_template("login.html", form=form)
        if not check_password_hash(user.password, form.password.data):
            form.password.errors.append("Password error")
            return render_template("login.html", form=form)
        flask_login.login_user(user)
        return redirect(url_for("user.main_page"))
    return render_template("login.html", form=form)


@user_blueprints.route("/main_page", methods=["GET", "GET"])
@flask_login.login_required
@db_session
def main_page():
    """
    主页面
    """
    return render_template("main_page.html", user_name=current_user.nickname,
                           user_role=current_user.role)


@user_blueprints.route("/logout", methods=["GET", "GET"])
@flask_login.login_required
@db_session
def logout():
    """
    注销
    """
    flask_login.logout_user()
    return redirect(url_for("user.login"))

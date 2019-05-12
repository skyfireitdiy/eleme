from functools import wraps
import flask_login
from flask import *
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import *
from database import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from pony.orm import *

user_blueprints = blueprints.Blueprint("user", "user", static_folder="static", template_folder="template",
                                       url_prefix="/user")


def merchant_required(func):
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
    return select(r for r in User if r.id == user_id).first()


class LoginForm(FlaskForm):
    nickname = StringField("昵称", validators=[DataRequired()])
    password = PasswordField("密码", validators=[DataRequired()])
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    nickname = StringField("昵称", validators=[DataRequired(), Length(1, 20, "昵称不大于20位")])
    name = StringField("姓名", validators=[DataRequired(), Length(1, 20, "姓名不大于20位")])
    password1 = PasswordField("密码", validators=[DataRequired(), Length(8, 16, "密码长度必须在8到16位")])
    password2 = PasswordField("确认密码", validators=[DataRequired(), EqualTo("password1", "密码不一致")])
    phone = StringField("电话", validators=[DataRequired(), Regexp(r"\d{6,13}", 0, "电话必须为6到13位数字")])
    address = StringField("地址", validators=[DataRequired()])
    role = SelectField("角色", choices=[('0', "商家"), ('1', "客户"), ('2', "配送员")])
    submit = SubmitField('注册')


@user_blueprints.route("/register", methods=["GET", "POST"])
@db_session
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if select(r for r in User if r.nickname == form.nickname.data).first() is not None:
            form.nickname.errors.append('用户 "%s" 已存在' % form.nickname.data)
            return render_template('register.html', form=form)
        User(
            nickname=form.nickname.data,
            name=form.name.data,
            password=generate_password_hash(form.password1.data),
            phone=form.phone.data,
            address=form.address.data,
            role=int(form.role.data))
        db.commit()
        flash('用户 "%s" 注册成功，请登录' % form.nickname.data)
        return redirect(url_for("user.login"))
    return render_template('register.html', form=form)


@user_blueprints.route("/login", methods=["GET", "POST"])
@db_session
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = select(r for r in User if r.nickname == form.nickname.data).first()
        if user is None:
            form.nickname.errors.append("用户不存在")
            return render_template("login.html", form=form)
        if not check_password_hash(user.password, form.password.data):
            form.password.errors.append("密码错误")
            return render_template("login.html", form=form)
        flask_login.login_user(user)
        if user.role == 0:
            return redirect(url_for("restaurant.manage"))
        return "登陆成功"
    return render_template("login.html", form=form)

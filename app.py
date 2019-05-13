import os

from flask import *
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from user import user_blueprints, get_user
from restaurant import restaurant_blueprints
from food import food_blueprints
from order import order_blueprints

app = Flask(__name__)

app.secret_key = os.urandom(32)
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = '/user/login'

csrf = CSRFProtect()

login_manager.init_app(app=app)
csrf.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """
    加载用户，这个函数由登录框架调用
    :param user_id:用户id
    :return: 用户对象
    """
    return get_user(user_id)


@app.route("/")
def index():
    """
    首页，跳转到登录界面
    :return: 登录重定向
    """
    return redirect(url_for("user.login"))


if __name__ == "__main__":
    """
    加载4个蓝图，每个蓝图实现在对应的py文件中，启动项目
    """
    app.register_blueprint(user_blueprints)
    app.register_blueprint(restaurant_blueprints)
    app.register_blueprint(food_blueprints)
    app.register_blueprint(order_blueprints)
    app.run(host="0.0.0.0", port=80, debug=False, use_reloader=True)

import os

from flask import *
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from user import user_blueprints, get_user
from restaurant import restaurant_blueprints
from food import food_blueprints

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
    return get_user(user_id)


if __name__ == "__main__":
    app.register_blueprint(user_blueprints)
    app.register_blueprint(restaurant_blueprints)
    app.register_blueprint(food_blueprints)
    app.run(host="0.0.0.0", port=80, debug=True, use_reloader=True)

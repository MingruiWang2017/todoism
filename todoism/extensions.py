from flask import request, current_app
from flask_babel import Babel, lazy_gettext as _l
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()
babel = Babel()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = _l('Please login in to access this page.')


@login_manager.user_loader
def load_user(user_id):
    from todoism.models import User
    return User.query.get(int(user_id))


@babel.localeselector
def get_locale():
    """区域获取函数，他会在处理每个请求时被调用"""
    if current_user.is_authenticated and current_user.locale is not None:
        return current_user.locale

    locale = request.cookies.get('locale')  # 匿名用户从cookie中寻找
    if locale is not None:
        return locale
    # 使用request的ACCEPT-LANGUAGES header匹配
    return request.accept_languages.best_match(current_app.config['TODOISM_LOCALES'])

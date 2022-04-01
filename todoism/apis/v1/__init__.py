from flask import Blueprint
from flask_cors import CORS

api_v1 = Blueprint('api_v1', __name__)

CORS(api_v1)  # 对api_v1下的所有url路由开启跨域支持， 允许来自任意源的跨域请求

from todoism.apis.v1 import resources

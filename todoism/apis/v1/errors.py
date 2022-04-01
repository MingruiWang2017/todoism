from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

from todoism.apis.v1 import api_v1


def api_abort(code, message=None, **kwargs):
    if message is None:
        message = HTTP_STATUS_CODES.get(code, '')  # 获取错误码对应的默认描述

    response = jsonify(code=code, message=message, **kwargs)
    response.status_code = code
    return response


def invalid_token():
    response = api_abort(401, error='invalid_token', error_description='Either the token was expired or invalid.')
    response.headers['WWW-Authenticate'] = 'Bearer'  # 定义用来访问该资源的认证方式为Bearer token
    return response


def token_missing():
    response = api_abort(401)
    response.headers['WWW-Authenticate'] = 'Bearer'
    return response


class ValidationError(ValueError):
    pass


@api_v1.errorhandler(ValidationError)
def validation_error(e):
    """当request参数解析错误时，自动捕获ValueError，返回400错误"""
    return api_abort(400, e.args[0])

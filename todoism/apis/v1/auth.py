from functools import wraps
import time
from datetime import datetime, timedelta

from flask import g, current_app, request
import authlib.jose.errors as j_errors
from authlib.jose import JsonWebToken

from todoism.apis.v1.errors import api_abort, invalid_token, token_missing
from todoism.models import User


class TokenExpireError(j_errors.JoseError):
    error = 'token_expired'


class InvalidTokenError(j_errors.JoseError):
    error = 'invalid_timed_Json_web_token_error'
    description = 'The token misses expiration '


class TimedJsonWebToken(JsonWebToken):
    expiration = 3600

    def __init__(self):
        super(TimedJsonWebToken, self).__init__()

    def encode(self, header, payload, key, expiration, check=True):
        if not expiration:
            expiration = self.expiration
        payload['exp'] = datetime.utcnow() + timedelta(seconds=expiration)
        payload['nbf'] = datetime.utcnow()
        payload['iat'] = datetime.utcnow()
        return super().encode(header, payload, key, check)

    def decode(self, s, key, claims_cls=None,
               claims_options=None, claims_params=None):
        try:
            claim = super().decode(s, key, claims_cls, claims_options, claims_params)
        except j_errors.JoseError as e:
            raise e
        # 判断token是否过期
        exp = claim.get('exp', None)
        if exp is None:
            raise InvalidTokenError()
        timestamp = int(time.time())
        if int(exp) < timestamp:
            raise TokenExpireError()
        return claim


def generate_token(user):
    expiration = 3600
    header = {'alg': 'HS256'}
    key = current_app.config['SECRET_KEY']
    payload = {'id': user.id}

    token = TimedJsonWebToken().encode(header, payload, key, expiration)
    return token, expiration


def validate_token(token):
    key = current_app.config['SECRET_KEY']
    try:
        data = TimedJsonWebToken().decode(token, key)
    except j_errors.JoseError:
        return False

    user = User.query.get(data['id'])
    if user is None:
        return False
    # 将user存储到全局变量g中，表示当前用户
    g.current_user = user
    return True


def get_token():
    """从request header中获取token。
    Flask只能解析Basic和Digest类型的authentication，所以需要自己手动处理token"""
    if 'Authorization' in request.headers:
        try:
            token_type, token = request.headers['Authorization'].split(None, 1)
        except ValueError:
            # Authorization header为空或者没有toekn时
            token_type = token = None
    else:
        token_type = token = None

    return token_type, token


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token_type, token = get_token()

        # 对于OPTIONS请求不必进行token验证，防止出现CORS问题
        if request.method != 'OPTIONS':
            if token_type is None or token_type.lower() != 'bearer':
                return api_abort(400, 'The token type must be bearer.')
            if token is None:
                return token_missing()
            if not validate_token(token):
                return invalid_token()
        return f(*args, **kwargs)

    return decorated

from authlib.jose import JsonWebToken
from datetime import datetime, timedelta


class TimedJsonWebToken(JsonWebToken):
    expiration = 3600

    def __init__(self):
        super(TimedJsonWebToken, self).__init__()

    def encode(self, header, payload, key, expiration, check=True):
        if not expiration:
            expiration = TimedJsonWebToken.expiration
        payload['exp'] = datetime.utcnow() + timedelta(seconds=expiration)
        payload['nbf'] = datetime.utcnow()
        payload['iat'] = datetime.utcnow()
        return super().encode(header, payload, key, check)

if __name__ == '__main__':
    header = {'alg': 'HS256'}
    key = '123456'
    token = TimedJsonWebToken().encode(header, {}, key, 300)
    print(token)
    import time
    print(time.time())

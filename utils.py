import datetime
import hmac
import base64
import hashlib


def datetime_to_epoch(_datetime: datetime.datetime) -> int:
    """Returns epoch in milliseconds for a datetime object"""

    return int(_datetime.strftime('%s')) * 1000


def generate_hmac_signature(hmac_key: str) -> (str, str):
    """Returns a tuple with the authorization_time string along with the signature to
    pass in the headers """

    authorization_time = datetime.datetime.now().strftime('%Y%m%dT%H%M%S%z')
    message = f'x-netflix-authorization-time={authorization_time}'
    secret_key = base64.b64decode(hmac_key)
    header_auth = hmac.new(secret_key, message.encode('utf-8'), digestmod=hashlib.sha256).digest()
    return authorization_time, base64.b64encode(header_auth).decode('utf-8')

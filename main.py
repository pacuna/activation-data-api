import requests
import base64
import hmac
import hashlib
import datetime
import json
import os

API_URL = 'https://examples.netflix.com/mvpdapi/v5/event/activations'
CREDENTIAL = os.getenv('CREDENTIAL')
HMAC_KEY = os.getenv('HMAC_KEY')


def datetime_to_epoch(_datetime: datetime.datetime) -> int:
    """Returns epoch in milliseconds for a datetime object"""

    return int(_datetime.strftime('%s')) * 1000


def generate_hmac_signature():
    """Returns a tuple with the authorization_time string correctly formatted along with the signature to
    pass in the headers """

    authorization_time = datetime.datetime.now().strftime('%Y%m%dT%H%M%S%z')
    message = f'x-netflix-authorization-time={authorization_time}'
    secret_key = base64.b64decode(HMAC_KEY)
    header_auth = hmac.new(secret_key, message.encode('utf-8'), digestmod=hashlib.sha256).digest()
    return authorization_time, base64.b64encode(header_auth).decode('utf-8')


def get_headers(authorization_time: str, signature: str) -> dict:
    return {
        'X-Netflix-AuthorizationTime': f'{authorization_time}',
        'X-Netflix-Header-Authorization': f'nflxv1 Credential={CREDENTIAL},Signature={signature}'
    }


def get_events(start: int, end: int = None) -> None:
    """Consumes Activation Events API.
    Receives start and end timestamps in epoch milliseconds.
    """

    # If no `end` is passed, we assume now() but with a delta of 3 hours for delay.
    if end is None:
        end = datetime_to_epoch(datetime.datetime.now() - datetime.timedelta(hours=3))

    if start > end:
        raise Exception("End date must be greater than start date")

    # Generate tuples with ranges spaced by maximum window of 30 days. We then can send a request for each tuple
    ranges = [(n, min(n + start, end)) for n in range(start, end, 2592000000)]

    for r in ranges:
        page = 0
        authorization_time, signature = generate_hmac_signature()
        payload = {
            'activatedAfterTimestamp': f'{r[0]}',
            'activatedBeforeTimestamp': f'{r[1]}',
        }

        headers = get_headers(authorization_time, signature)
        print(headers)
        req = requests.get(f'{API_URL}', params=payload, headers=headers)

        # Only create a file if there are activationEvents in the response
        if 'activationEvents' in req.json() and len(req.json()['activationEvents']) > 0:
            with open(f'{r[0]}-{r[1]}-page{page}.json', 'w') as f:
                json.dump(req.json()['activationEvents'], f)

        # Check if we have paginated results and iterate until the last page
        while 'next' in req.json():
            page += 1
            _next = req.json()['next']
            authorization_time, signature = generate_hmac_signature()
            headers = get_headers(authorization_time, signature)
            req = requests.get(f'{API_URL}?{_next}', headers=headers)

            # Only create a file if there are activationEvents in the response
            if 'activationEvents' in req.json() and len(req.json()['activationEvents']) > 0:
                with open(f'{r[0]}-{r[1]}-page{page}.json', 'w') as f:
                    json.dump(req.json()['activationEvents'], f)

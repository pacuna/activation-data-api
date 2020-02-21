import requests
import datetime
import json
import os
from utils import generate_hmac_signature, datetime_to_epoch

API_URL = 'https://examples.netflix.com/mvpdapi/v5/event/activations'
CREDENTIAL = os.getenv('CREDENTIAL')
HMAC_KEY = os.getenv('HMAC_KEY')


class APIService:

    def get_events(self, after: int, before: int = None) -> None:
        """Consumes Activation Events API.
        Receives start and end timestamps in epoch milliseconds.
        Creates one file per every 30days interval contained in the range.
        """

        # If no `end` is passed, we assume now() but with a delta of 3 hours for delay.
        max_end = datetime_to_epoch(datetime.datetime.now() - datetime.timedelta(hours=3))

        if before is None:
            before = max_end

        if before is not None and before > max_end:
            raise Exception("End datetime must be less than three hours back from now")

        if after > before:
            raise Exception("End date must be greater than start date")

        # Generate tuples with ranges spaced by maximum window of 30 days. We then can send a request for each tuple
        # Can run in parallel depending on the throttling per client
        ranges = [(n, min(n + after, before)) for n in range(after, before, 2592000000)]

        for r in ranges:
            page = 0
            authorization_time, signature = generate_hmac_signature(HMAC_KEY)
            payload = {
                'activatedAfterTimestamp': f'{r[0]}',
                'activatedBeforeTimestamp': f'{r[1]}',
            }
            headers = {
                'X-Netflix-AuthorizationTime': f'{authorization_time}',
                'X-Netflix-Header-Authorization': f'nflxv1 Credential={CREDENTIAL},Signature={signature}'
            }

            # Make initial request, no page and no `next` string in the url
            req = requests.get(f'{API_URL}', params=payload, headers=headers)

            if req.status_code != 200:
                return req.json()['responseStatus']

            # Only create a file if there are activationEvents in the response
            # The format of the file is `start`-`end`-`page`.json`
            if 'activationEvents' in req.json() and len(req.json()['activationEvents']) > 0:
                with open(f'{r[0]}-{r[1]}-{page}.json', 'w') as f:
                    json.dump(req.json()['activationEvents'], f)

            # Check if we have paginated results and iterate until the last page. If `next` is present
            # we can use its value as the query param for the subsequent requests.
            while 'next' in req.json():
                page += 1
                _next = req.json()['next']
                authorization_time, signature = generate_hmac_signature(HMAC_KEY)
                headers = {
                    'X-Netflix-AuthorizationTime': f'{authorization_time}',
                    'X-Netflix-Header-Authorization': f'nflxv1 Credential={CREDENTIAL},Signature={signature}'
                }
                req = requests.get(f'{API_URL}?{_next}', headers=headers)

                if req.status_code != 200:
                    return req.json()['responseStatus']

                if 'activationEvents' in req.json() and len(req.json()['activationEvents']) > 0:
                    with open(f'{r[0]}-{r[1]}-{page}.json', 'w') as f:
                        json.dump(req.json()['activationEvents'], f)


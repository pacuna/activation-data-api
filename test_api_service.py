import pytest
import responses
import os
import datetime
from api_service import APIService, API_URL
from utils import datetime_to_epoch


class TestApiService:

    def test_start_is_greater_than_end_raises_error(self):
        service = APIService()
        start = 1577901600000
        end = 1546365600000

        with pytest.raises(Exception) as e:
            service.get_events(start, end)
        assert "End date must be greater than start date" == str(e.value)

    def test_end_is_greater_than_three_hours_back_from_now_raises_error(self):
        service = APIService()
        start = 1577901600000
        end = datetime_to_epoch(datetime.datetime.now() - datetime.timedelta(hours=1))

        with pytest.raises(Exception) as e:
            service.get_events(start, end)
        assert "End datetime must be less than three hours back from now" == str(e.value)

    @responses.activate
    def test_response_with_no_next(self):
        service = APIService()
        start = 1546369200000
        end = 1546376400000
        response = {
            "activationEvents": [
                {
                    "pai": "acbde",
                    "activationTimestamp": "1546369200000"
                },
                {
                    "pai": "acbde",
                    "activationTimestamp": "1546372800000"
                },
                {
                    "pai": "acbde",
                    "activationTimestamp": "1546376400000"
                }
            ],
            "activatedBeforeTimestamp": "1546380000000",
            "responseStatus": {
                "httpStatusCode": 200
            }
        }
        responses.add(
            method='GET',
            url=API_URL,
            json=response
        )
        service.get_events(start, end)
        assert os.path.exists(f'{start}-{end}-0.json')
        os.remove(f'{start}-{end}-0.json')

    @responses.activate
    def test_response_with_no_events_does_not_create_file(self):
        service = APIService()
        start = 1546369200000
        end = 1546376400000
        response = {
            "activationEvents": [
            ],
            "activatedBeforeTimestamp": "1546380000000",
            "responseStatus": {
                "httpStatusCode": 200
            }
        }
        responses.add(
            method='GET',
            url=API_URL,
            json=response
        )
        service.get_events(start, end)
        assert not os.path.exists(f'{start}-{end}-0.json')

    @responses.activate
    def test_response_with_with_next(self):
        service = APIService()
        start = 1546369200000
        end = 1546376400000
        response_with_next = {
            "activationEvents": [
                {
                    "pai": "acbde",
                    "activationTimestamp": "1546369200000"
                },
                {
                    "pai": "acbde",
                    "activationTimestamp": "1546372800000"
                },
                {
                    "pai": "acbde",
                    "activationTimestamp": "1546376400000"
                }
            ],
            "activatedBeforeTimestamp": "1546380000000",
            "responseStatus": {
                "httpStatusCode": 200
            },
            "next": "activatedAfterTimestamp=1546369200000&activatedBeforeTimestamp=1546376400000&page=1"
        }
        response_without_next = {
            "activationEvents": [
                {
                    "pai": "acbde",
                    "activationTimestamp": "1546369200000"
                },
                {
                    "pai": "acbde",
                    "activationTimestamp": "1546372800000"
                },
                {
                    "pai": "acbde",
                    "activationTimestamp": "1546376400000"
                }
            ],
            "activatedBeforeTimestamp": "1546380000000",
            "responseStatus": {
                "httpStatusCode": 200
            }
        }
        responses.add(
            method='GET',
            url=f'{API_URL}?activatedAfterTimestamp=1546369200000&activatedBeforeTimestamp=1546376400000',
            json=response_with_next,
        )
        responses.add(
            method='GET',
            url=f'{API_URL}?activatedAfterTimestamp=1546369200000&activatedBeforeTimestamp=1546376400000&page=1',
            json=response_without_next,
        )
        service.get_events(start, end)
        assert os.path.exists(f'{start}-{end}-0.json')
        assert os.path.exists(f'{start}-{end}-1.json')
        os.remove(f'{start}-{end}-0.json')
        os.remove(f'{start}-{end}-1.json')

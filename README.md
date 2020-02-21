# Activation Data API

## Requirements

- Python 3.6+
- pip

You can create your own virtual environment to install the dependencies
and run this project with:

```bash
python -m venv venv # or python3
source venv/bin/activate
```

## Usage

Install requirements:

```bash
pip install -r requirements.txt
```

Set these two environment variables:

```
CREDENTIAL=<PARTNER>
HMAC_KEY=<SECRET_KEY>
```

Set the `API_URL` variable in `api_service.py`.

To fetch the events between 2 timestamps in epoch milliseconds:

```python
from api_service import APIService


service = APIService()
after = 1580521757000
before = 1581299357000

service.get_events(after, before)
```

This will generate one file per every maximum window range (30 days) and
for every page.

## Run tests

```bash
python -m pytest tests.py
```

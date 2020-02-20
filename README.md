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

Set the `API_URL` variable and now you can use the `get_events()` method from `main.py`.

## Run tests

```bash
python -m pytest tests.py
```

## Recommendations

- Catch requests errors.
- Extract common methods to a library to avoid duplication.
- Don't manage sensitive data in the code. Use other mechanism such as environmental variables.
- Use mock responses of the API to test your code
- Propagate the status code responses from the API to inspect results and errors.


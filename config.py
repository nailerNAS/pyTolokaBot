import json
from os import getenv


def cookies_converter(s: str) -> dict:
    return json.loads(s)


def get(key, default=None, converter=None):
    value = getenv(key, default)

    return converter(value) if converter else value


TOKEN = get('TOKEN')
USE_WEBHOOK = get('USE_WEBHOOK', False, bool)
WEBHOOK_HOST = get('WEBHOOK_HOST')
WEBHOOK_PORT = get('WEBHOOK_PORT', converter=int)
WEBHOOK_LOCAL_PORT = get('PORT', converter=int)
WEBHOOK_PATH = get('WEBHOOK_PATH')
WEBHOOK_URL = f'https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}'
CUSTOM_SSL_CERT = get('CUSTOM_SSL_CERT', False, bool)
SSL_CERT = get('SSL_CERT')
SSL_PRIV = get('SSL_PRIV')

COOKIES = get('COOKIES', converter=cookies_converter)
CHANNEL = get('CHANNEL', converter=int)

HEROKU = get('HEROKU', False, bool)

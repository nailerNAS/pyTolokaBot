import json
from os import getenv


def cookies_converter(s: str) -> dict:
    return json.loads(s)


def get(key, default=None, converter=None):
    value = getenv(key, default)

    return converter(value) if converter else value


TOKEN = get('TOKEN')
USE_WEBHOOK = get('USE_WEBHOOK', False, bool)

if USE_WEBHOOK:
    WEBHOOK_HOST = get('WEBHOOK_HOST')
    WEBHOOK_PORT = get('WEBHOOK_PORT', converter=int)
    WEBHOOK_LOCAL_PORT = get('PORT', converter=int)
    WEBHOOK_PATH = get('WEBHOOK_PATH')
    WEBHOOK_URL = f'https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}'

COOKIES = get('COOKIES', converter=cookies_converter)
CHANNEL = get('CHANNEL', converter=int)

from os import getenv


def get(key, default=None, converter=None):
    value = getenv(key, default)

    return converter(value) if converter else value


TOKEN = get('TOKEN')
USE_WEBHOOK = get('USE_WEBHOOK', False, bool)

if USE_WEBHOOK:
    WEBHOOK_HOST = get('WEBHOOK_HOST')
    WEBHOOK_PORT = get('WEBHOOK_PORT', converter=int)
    WEBHOOK_PATH = get('WEBHOOK_PATH')
    WEBHOOK_URL = f'https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}'

COOKIES = get('COOKIES')
CHANNEL = get('CHANNEL', converter=int)

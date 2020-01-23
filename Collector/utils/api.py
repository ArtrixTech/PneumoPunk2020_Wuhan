import requests

from utils.specs import *


def api_concat(api_url, *args):
    assert isinstance(api_url, str)

    params_count = len(api_url.split('%param')) - 1
    assert len(args) == params_count
    for i in range(1, params_count + 1):
        api_url = api_url.replace("%%param%s%%" % str(i), str(args[i - 1]))
    return api_url


def api_fetch(api_url, *args):
    def fetch(retry=False):
        try:
            url = api_concat(api_url, *args)
            request = requests.get(url, headers=HEADERS)
            request.encoding = 'utf-8'
            content = request.text

            return content

        except ValueError:
            if not retry:
                return fetch(retry=True)
            return False

    return fetch()

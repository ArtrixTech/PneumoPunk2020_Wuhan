import json

import requests

from utils.specs import *


def api_concat(api_url, *args):
    assert isinstance(api_url, str)

    params_count = len(api_url.split('%param')) - 1
    assert len(args) == params_count
    for i in range(1, params_count + 1):
        api_url = api_url.replace("%%param%s%%" % str(i), str(args[i - 1]))
    return api_url


def buff_api_fetch(api_url, *args):
    def fetch(retry=False):
        try:
            url = api_concat(api_url, *args)
            request = requests.get(url, headers=HEADERS)
            request.encoding = 'utf-8'
            content = request.text

            if '502 Bad Gateway' in content:
                raise ValueError('[Buff API Fetch] Error in fetching, args: %s' % args)

            jsonified = json.loads(content)

            if jsonified['code'] == 'OK':
                return jsonified
            raise ValueError('[Buff API Fetch] Error in fetching, args: %s' % args)
        except ValueError:
            if not retry:
                return fetch(retry=True)
            return False

    return fetch()


def steam_price_fetch(api_url, *args):
    def fetch(retry=False):
        try:
            url = api_concat(api_url, *args)
            request = requests.get(url, headers=HEADERS)
            request.encoding = 'utf-8'
            content = request.text

            if 'null' in content:
                raise ValueError('[Steam API Fetch] Error in fetching, args: %s' % args)

            jsonified = json.loads(content)

            if jsonified['success'] == True:
                return jsonified
            raise ValueError('[Steam API Fetch] Error in fetching, args: %s' % args)
        except ValueError:
            if not retry:
                return fetch(retry=True)
            return False
        except TypeError:
            print(content)

    return fetch()

import random
import time
from datetime import datetime

from utils import api_list
from utils.api import *
from utils.denoise import *
from utils.exception_retry import retry
from utils.log import Log
from utils.specs import *


def is_metadata_obj(obj):
    return isinstance(obj, WeaponMetadata)


def is_weapon_obj(obj):
    return isinstance(obj, Weapon)


class WeaponMetadata:

    def sql_values(self):
        rt_tuple = (str(self.item_name if hasattr(self, 'item_name') else '#DataNotFound#'),
                    str(self.buff_id if hasattr(
                        self, 'buff_id') else '#DataNotFound#'),
                    str(self.meta_data_refreshed_time if hasattr(self,
                                                                 'meta_data_refreshed_time') else '#DataNotFound#'),
                    str(self.type if hasattr(self, 'type') else '#DataNotFound#'),
                    str(self.exhibition_image if hasattr(
                        self, 'exhibition_image') else '#DataNotFound#'),
                    str(self.steam_market_url if hasattr(self, 'steam_market_url') else '#DataNotFound#'))

        return rt_tuple

    def __init__(self, buff_id, db):
        self.buff_id = buff_id
        self.logger = Log('Weapon-Metadata')

        query_result = db.query_weapon_metadata(buff_id)

        if not query_result[0]:

            url = api_concat(api_list.BUFF_SELL_ORDER_API, buff_id)
            request = requests.get(url, headers=HEADERS, cookies=COOKIES)
            request.encoding = 'utf-8'
            content = request.text

            if content:
                jsonified = json.loads(content)

                if jsonified['code'] == 'OK':

                    item = jsonified['data']['goods_infos'][str(buff_id)]

                    try:

                        self.item_name = item['name']
                        self.meta_data_refreshed_time = time.time()
                        self.steam_market_url = 'https://steamcommunity.com/market/listings/730/' + str(
                            item['market_hash_name']).replace(' ', '%20')
                        self.exhibition_image = item['icon_url']
                        self.type = item['tags']['category']['internal_name']

                    # In case of single column of data-loss, keep it the False value.
                    # This error will be sent to database to save as NULL value.
                    except KeyError:
                        self.logger.log(
                            'Item %s does not contain some value.' % self.item_name)

                else:
                    raise ValueError('[WeaponMetadata] Buff fetch error.')
            else:
                raise ValueError('Buff returned nothing.')
        else:
            self.item_name, self.meta_data_refreshed_time, self.steam_market_url, self.exhibition_image, self.type = \
                (query_result[1][0][0], query_result[1][0][2], query_result[1][0][5], query_result[1][0][4],
                 query_result[1][0][3])


class Weapon:

    def sql_values(self):
        rt_tuple = (self.metadata.item_name,
                    self.metadata.buff_id,
                    self.update_timestamp,
                    str(self.buff_trade_history).replace("'", "#%"),
                    # Includes time, price, paint_wear
                    self.buff_selling_duration,
                    self.buff_buy_price,
                    self.buff_sell_price,
                    self.steam_buy_price,
                    self.steam_sell_price,
                    self.buff_profit_ratio,
                    self.steam_profit_ratio,
                    self.buff_history_trade_price_median,
                    self.buff_history_trade_price_std_error,
                    self.buff_in_stock_count)
        return str(rt_tuple).replace("'", "\"").replace("#%", "'")

    def save_to_database(self):
        # self.db.insert_item_record(self.metadata.buff_id, self.sql_values())
        self.db.update_item_data(self.metadata.buff_id, self.sql_values())

    def get_last_update_delta_time(self):
        success, result = self.db.query_realtime_data(
            self.metadata.buff_id, 'update_time')
        success = bool(result[0]) if success else False
        success = bool(result[0][0]) if success else False

        return False if not success else int(time.time()) - int(result[0][0])

    def __init__(self, buff_id, db, refresh_limit=0):

        self.db = db
        self.metadata = WeaponMetadata(buff_id, self.db)

        # self.db.create_item_table_if_not_exist(self.metadata.buff_id)

        self.update_timestamp = -1
        self.buff_in_stock_count = 0
        self.buff_buy_price = 0
        self.steam_buy_price = 0
        self.buff_trade_history = {'history': []}
        self.buff_selling_duration = 0
        self.buff_history_trade_price_median, self.buff_history_trade_price_std_error = 0, 0

        self.buff_sell_price = 0
        self.steam_sell_price = 0
        self.buff_profit_ratio = 0
        self.steam_profit_ratio = 0

        self.update_data(refresh_limit=refresh_limit)

        # self.buff_sell_price = self.buff_buy_price * 0.965
        # self.steam_sell_price = self.steam_buy_price * 0.75

        # self.buy_profit_ratio = float(self.steam_sell_price) / float(self.buff_buy_price)
        # self.sell_profit_ratio = float(self.buff_sell_price) / float(self.steam_buy_price)

    def update_data(self, refresh_limit=0):

        do_flag = True
        if refresh_limit:
            delta_t = self.get_last_update_delta_time()
            do_flag = delta_t > refresh_limit if delta_t else True

        if do_flag:

            # bill_result = buff_api_fetch(api_list.BUFF_BILL_ORDER_API, self.metadata.buff_id)
            bill_result = retry(
                buff_api_fetch, 5, api_list.BUFF_BILL_ORDER_API, self.metadata.buff_id)

            sell_result = retry(
                buff_api_fetch, 5, api_list.BUFF_SELL_ORDER_API, self.metadata.buff_id)

            get_steam = False

            if get_steam:
                steam_price_result = retry(
                    steam_price_fetch, 5, api_list.STEAM_PRICE_URL2, str(self.metadata.steam_market_url).replace(
                        'https://steamcommunity.com/market/listings/730/', ''))

                if 'median_price' in steam_price_result:
                    self.steam_buy_price = float(
                        steam_price_result['median_price'].replace('¥ ', '').replace(',', ''))
                else:
                    self.steam_buy_price = float(
                        steam_price_result['lowest_price'].replace('¥ ', '').replace(',', ''))
            else:
                for key in sell_result['data']['goods_infos']:
                    self.steam_buy_price = float(
                        sell_result['data']['goods_infos'][key]['steam_price_cny'])
                    break

            self.update_timestamp = int(time.time())

            # Todo:Bug fix
            self.buff_in_stock_count = int(sell_result['data']['total_count'])
            self.buff_buy_price = float(sell_result['data']['items'][0]['price']) if len(
                sell_result['data']['items']) else -1  # Buy price only use the lowest price.

            # Buff trade history fetching & Selling price median / std_error fetching
            self.buff_trade_history = {'history': []}
            time_shift = 0
            price_list = []
            bill_items = bill_result['data']['items']

            for item in bill_items:
                delta_time = int(time.mktime(
                    datetime.now().date().timetuple())) - int(item['buyer_pay_time'])
                time_shift += delta_time

                price_list.append(float(item['price']))

                self.buff_trade_history['history'].append(
                    {'price': float(item['price']), 'sold_time': int(item['buyer_pay_time']), 'delta_time': delta_time})

            self.buff_selling_duration = time_shift / \
                                         len(bill_items) if len(bill_items) else -1
            self.buff_history_trade_price_median, self.buff_history_trade_price_std_error = get_median(
                price_list), get_std(price_list)

            if self.buff_history_trade_price_median == -1:
                self.buff_history_trade_price_median = self.buff_buy_price

            self.buff_sell_price = self.buff_buy_price * \
                                   0.965 if self.buff_buy_price > 0 else -1
            self.steam_sell_price = self.steam_buy_price * \
                                    0.86958 if self.steam_buy_price > 0 else -1

            self.buff_profit_ratio = self.buff_sell_price / \
                                     self.steam_buy_price if self.steam_buy_price > 0 else 0
            self.steam_profit_ratio = self.steam_sell_price / \
                                      self.buff_buy_price if self.buff_buy_price > 0 else 0

            self.save_to_database()
            print('    saved.')
        else:
            print('    skipped.')

    def outdated():
        def get_buff_trade_history(self, buff_id, retry=False):
            url = 'https://buff.163.com/api/market/goods/bill_order?game=csgo&goods_id=' + \
                  str(buff_id)
            request = requests.get(url, headers=HEADERS)
            request.encoding = 'utf-8'
            content = request.text

            print(content)

            jsonified = json.loads(content)

            if jsonified['code'] == 'OK':

                result = []

                items = jsonified['data']['items']

                for item in items:
                    result.append(
                        {'price': float(item['price']), 'sold_time': int(item['buyer_pay_time'])})

                return json.dumps(result)

            else:
                print(' [WeaponClass] Fetch buff price failed.')

        def get_buff_in_stock_list(self, buff_id, retry=False):

            try:

                url = BUFF_SELL_ORDER_API.replace('%id%', str(buff_id))
                request = requests.get(url, headers=HEADERS)
                request.encoding = 'utf-8'
                content = request.text

                jsonified = json.loads(content)

                if jsonified['code'] == 'OK':
                    price = []
                    items = jsonified['data']['items']

                    for item in items:
                        price.append(float(item['price']))

                    if len(price) == 0:
                        price = [-1]

                    return price
                else:
                    print(' [WeaponClass] Fetch buff price failed.')
                    raise ValueError

            except ValueError:
                if not retry:
                    print('[Limitation] Buff price fetch error,sleeping...')
                    time.sleep(random.randrange(15, 25) / 10)
                    return self.get_buff_in_stock_list(buff_id, retry=True)
                return False

            except ConnectionError:
                if not retry:
                    print('[Limitation] Buff price fetch error,sleeping...')
                    time.sleep(random.randrange(15, 25) / 10)
                    return self.get_buff_in_stock_list(buff_id, retry=True)
                return False

        def get_steam_price(self, steam_url, retry_request=False, retry_price=False):

            try:
                request = requests.get(STEAM_PRICE_URL2.replace('%name%', str(steam_url).replace(
                    'https://steamcommunity.com/market/listings/730/', '')), headers=HEADERS, timeout=5)
            except requests.exceptions.SSLError:
                if not retry_request:
                    print('[SSL Error] Steam price fetch error,sleeping...')
                    time.sleep(random.randrange(2, 4) * 0.5)
                    return self.get_steam_price(steam_url, retry_request=True)
                return False

            except requests.exceptions.ReadTimeout:
                if not retry_request:
                    print('[SSL Error] Steam price fetch error,sleeping...')
                    time.sleep(random.randrange(2, 4) * 0.5)
                    return self.get_steam_price(steam_url, retry_request=True)
                return False

            except requests.exceptions.ProxyError:
                # Infinitely retry the proxy error.
                print(
                    '[Proxy Error] Steam price fetch error,sleeping... '
                    '[ If this error shows frequently, plz check the proxy server. ]')
                time.sleep(random.randrange(2, 4) * 0.5)
                return self.get_steam_price(steam_url, retry_request=True)

            request.encoding = 'utf-8'
            content = request.text

            jsonified = json.loads(content)

            try:
                if jsonified['success']:
                    price = jsonified['median_price'].replace('¥ ', '')
                    # time.sleep(random.randrange(10, 20) / 10)
                    return float(price)
                print(' [WeaponClass] Fetch steam price failed.')
                return False
            except TypeError:
                if not retry_price:
                    print('[Limitation] Steam price fetch error,sleeping...')
                    time.sleep(random.randrange(2, 4) * 0.5)
                    return self.get_steam_price(steam_url, retry_price=True)
                return False

            except KeyError:
                # This error was caused by non-sold-record items. The API returns only the lowest price.
                return False

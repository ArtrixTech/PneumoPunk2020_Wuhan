# Param1: page_number Param2: minimum_price Param3: maximum_price
BUFF_ITEM_API = 'https://buff.163.com/api/market/goods?game=csgo&page_num=%param1%&min_price=%param2%&max_price=%param3%'

# Param1: goods_id
BUFF_SELL_ORDER_API = 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=%param1%&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1'

# Param1: goods_id
BUFF_BILL_ORDER_API = 'https://buff.163.com/api/market/goods/bill_order?game=csgo&goods_id=%param1%&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1'

STEAM_PRICE_URL = 'https://steamcommunity.com/market/itemordershistogram?country=CN&language=schinese&currency=23&item_nameid=%steam_id%&two_factor=0'
STEAM_PRICE_URL2 = 'https://steamcommunity.com/market/priceoverview/?currency=23&appid=730&market_hash_name=%param1%'

import flask
from flask import Blueprint

from utils.database import *

back_blueprint = Blueprint('back_end', __name__)
db = CSGODatabase("mysql.artrix.tech", "csgo", "csgo", "CSGO", charset='utf8', port=33066)


@back_blueprint.route('/get_sell_recommend')
def get_sell_recommend():
    sql = CSGOSql()
    sql.select('realtime_data.name, realtime_data.buff_id, type, update_time,'
               'buff_selling_duration, buff_in_stock_count, buff_buy_price, buff_sell_price, '
               'steam_buy_price, steam_sell_price, buff_profit_ratio, steam_profit_ratio,'
               'buff_history_trade_price_std_error', 'weapon_meta_data, realtime_data') \
        .where(
        'buff_buy_price > 15 and buff_buy_price <200 and buff_in_stock_count > 15 and realtime_data.buff_id = weapon_meta_data.buff_id')
    sql.order('steam_profit_ratio').limit(180)

    return flask.make_response(db.db.execute_with_json_return(sql))

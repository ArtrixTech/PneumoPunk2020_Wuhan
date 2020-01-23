import flask
from flask import Blueprint

from utils.database import *

back_blueprint = Blueprint('back_end', __name__)
dbf = DatabaseOperation("mysql.artrix.tech", "csgo", "csgo", "CSGO", charset='utf8', port=33066)


@back_blueprint.route('/get_history')
def get_sell_recommend():
    sql = SqlCommand()
    sql.select('time,region,sceptical,death,infected,cured', 'data_record')
    sql.order('time').limit(5)

    return flask.make_response(dbf.execute_with_json_return(sql))

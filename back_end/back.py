import json

import flask
from flask import Blueprint

from utils.database import *

back_blueprint = Blueprint('back_end', __name__)
dbf = DatabaseOperation("mysql.artrix.tech", "pneu2020", "pneu2020",
                        "pneu2020", charset='utf8', port=33069)


def execute_with_json_return(db, sql_command):
    assert isinstance(sql_command, SqlCommand)

    keys = str(sql_command.select_param[0]).split(',')

    flag, result = db.execute(str(sql_command))
    db.commit()

    if flag:
        rt_list = {'code': 0,
                   'count': len(result),
                   'start_time': min(item[keys.index('time')] for item in result),
                   'msg': "",
                   'data': []}

        for item in result:

            item_dict = {}
            index = 0
            for data in item:
                item_dict[keys[index].replace(" ", "")] = data
                index += 1

            rt_list['data'].append(item_dict)
        return json.dumps(rt_list)
    return {'code': 400, 'count': 0, 'msg': "Database Error."}


@back_blueprint.route('/get_history')
def get_sell_recommend():
    sql = SqlCommand()
    sql.select('region,time,infected,death,sceptical,cured', 'data_record')
    sql.order('time').limit(500)
    print('fetching...')
    return flask.make_response(execute_with_json_return(dbf, sql))

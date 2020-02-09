import json

import flask
from flask import Blueprint
from flask_cors import CORS

from utils.database import *

back_blueprint = Blueprint('back_end', subdomain='api', import_name=__name__)
dbf = DatabaseOperation("mysql.artrix.tech", "pneu2020", "pneu",
                        "pneu2020", charset='utf8', port=33069)
CORS(back_blueprint)


def linux_timespan_to_js(linux_ts):
    return int(str(linux_ts) + '000')


def execute_with_json_return(db, sql_command):
    assert isinstance(sql_command, SqlCommand)

    keys = str(sql_command.select_param[0]).split(',')

    try:
        flag, result = db.execute(str(sql_command))
        db.commit()

        if flag:
            rt_list = {'code': 0,
                       'count': len(result),
                       'start_time': linux_timespan_to_js(min(item[keys.index('time')] for item in result)),
                       # 'start_time': min(item[keys.index('time')] for item in result),
                       'msg': "",
                       'data': []}

            for item in result:

                item_dict = {}
                index = 0
                for data in item:
                    item_name = keys[index].replace(" ", "")

                    if item_name == 'time':
                        item_dict[item_name] = linux_timespan_to_js(data)
                    else:
                        item_dict[item_name] = data
                    index += 1

                rt_list['data'].append(item_dict)
            return json.dumps(rt_list)
        return json.dumps({'code': 400, 'count': 0, 'msg': "Database Error."})
    except:
        db.reconnect()
        return json.dumps({'code': 400, 'count': 0, 'msg': "Database Error."})


@back_blueprint.route('/get_history')
def get_history():
    sql = SqlCommand()
    sql.select('time,infected,death,sceptical,cured', 'data_record')
    sql.order('time').limit(2000)
    print('fetching...')
    return flask.make_response(execute_with_json_return(dbf, sql))

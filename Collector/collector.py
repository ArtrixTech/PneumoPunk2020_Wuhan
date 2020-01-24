import json
import time

from utils.api import *
from utils.api_list import *
from utils.cut_string import cut_string
from utils.database import DatabaseOperation
from utils.exception_retry import retry

db = DatabaseOperation("mysql.artrix.tech", "pneu2020", "pneu2020",
                       "pneu2020", charset='utf8', port=33069)

last_time = None
last_data = ()
SLEEP_DELAY = 10  # Unit: second
while True:
    skip_flag = False
    content = retry(api_fetch, 2, DXY_URL)
    overview = '{' + cut_string(content, 'window.getStatisticsService = {', '}') + '}'
    overview_json = None
    try:
        overview_json = json.loads(overview)
    except json.decoder.JSONDecodeError:
        skip_flag = True

    if not skip_flag and overview_json:

        modify_time = int(str(overview_json['modifyTime']).strip('000'))
        if not last_time == modify_time:
            region = str(overview_json['id'])
            image_url = overview_json['imgUrl']
            count_describe_text = overview_json['countRemark']

            infected = cut_string(count_describe_text, '确诊', '例').strip('\' ')
            sceptical = cut_string(count_describe_text, '疑似', '例').strip('\' ')
            cured = cut_string(count_describe_text, '治愈', '例').strip('\' ')
            death = cut_string(count_describe_text, '死亡', '例').strip('\' ')


            def data_equal(tuple1, tuple2):

                def exist_in_tuple(tuple_input, data):
                    assert isinstance(tuple_input, tuple)
                    try:
                        i = tuple_input.index(data)
                        return True
                    except ValueError:
                        return False

                assert isinstance(tuple1, tuple) and isinstance(tuple2, tuple)
                if len(tuple1) == len(tuple2):
                    for item in tuple1:
                        if not exist_in_tuple(tuple2, item):
                            return False
                    return True
                return False


            data = (modify_time, region, infected, death, sceptical, cured, image_url)
            data_str = str(data)

            if not data_equal(data[1:], last_data[1:]):
                db.insert_item_data('data_record', data_str)

            last_data = data
            last_time = modify_time

    time.sleep(SLEEP_DELAY)

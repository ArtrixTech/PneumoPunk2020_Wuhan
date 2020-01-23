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
SLEEP_DELAY = 10  # Unit: second
while True:
    content = retry(api_fetch, 2, DXY_URL)
    overview = '{' + cut_string(content, 'window.getStatisticsService = {', '}') + '}'
    overview_json = json.loads(overview)

    modify_time = int(str(overview_json['modifyTime']).strip('000'))
    if not last_time == modify_time:
        region = str(overview_json['id'])
        image_url = overview_json['imgUrl']
        count_describe_text = overview_json['countRemark']

        infected = cut_string(count_describe_text, '确诊', '例').strip('\' ')
        sceptical = cut_string(count_describe_text, '疑似', '例').strip('\' ')
        cured = cut_string(count_describe_text, '治愈', '例').strip('\' ')
        death = cut_string(count_describe_text, '死亡', '例').strip('\' ')

        db.insert_item_data('data_record', str(
            (modify_time, region, infected, death, sceptical, cured, image_url)))

        last_time = modify_time

    time.sleep(SLEEP_DELAY)

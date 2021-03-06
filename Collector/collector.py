import json
import time

import pymysql

from utils.api import *
from utils.api_list import *
from utils.cut_string import cut_string
from utils.database import DatabaseOperation
from utils.exception_retry import retry

db = DatabaseOperation("mysql.artrix.tech", "pneu2020", "pneu",
                       "pneu2020", charset='utf8', port=33069)

last_time = None
last_overview_data = ()
SLEEP_DELAY = 30  # Unit: second


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


def analyze_overview_updated(json_data):
    modify_time = int(str(json_data['modifyTime'])[:-3])
    if not last_time == modify_time:
        region = str(json_data['id'])
        image_url = json_data['imgUrl']

        infected = json_data['confirmedCount']
        serious = json_data['seriousCount']
        sceptical = json_data['suspectedCount']
        cured = json_data['curedCount']
        death = json_data['deadCount']

        data = (modify_time, infected, serious, death, sceptical, cured, image_url)
        data_str = str(data)

        if not data_equal(data[1:], last_overview_data[1:]):
            db.insert_item_data('data_record', data_str)
        else:
            print('Unchanged')

        return data, modify_time
    return last_overview_data, modify_time


def analyze_overview(json_data):
    modify_time = int(str(json_data['modifyTime'])[:-3])
    if not last_time == modify_time:
        region = str(json_data['id'])
        image_url = json_data['imgUrl']
        count_describe_text = json_data['countRemark']

        infected = cut_string(count_describe_text, '确诊', '例').strip('\' ')
        sceptical = cut_string(count_describe_text, '疑似', '例').strip('\' ')
        cured = cut_string(count_describe_text, '治愈', '例').strip('\' ')
        death = cut_string(count_describe_text, '死亡', '例').strip('\' ')

        data = (modify_time, infected, death, sceptical, cured, image_url)
        data_str = str(data)

        if not data_equal(data[1:], last_overview_data[1:]):
            db.insert_item_data('data_record', data_str)
        else:
            print('Unchanged')

        return data, modify_time
    return last_overview_data, modify_time


last_province_data = {}
province_modify_bool = {}
province_names = ['湖北省', '浙江省', '广东省', '河南省', '重庆市', '湖南省', '安徽省', '北京市', '上海市', '山东省', '江西省', '广西壮族自治区', '江苏省', '四川省',
                  '海南省', '辽宁省', '福建省', '黑龙江省', '陕西省', '河北省', '云南省', '天津市', '山西省', '内蒙古自治区', '甘肃省', '贵州省', '香港',
                  '宁夏回族自治区', '吉林省', '新疆维吾尔自治区', '台湾', '澳门', '青海省']


def analyze_province(json_data, modify_time):
    def comp_prov_data(prov_data1, prov_data2):
        for key in prov_data1:
            if not key == 'cities':  # Only compare summary data
                if not prov_data2[key] == prov_data1[key]:
                    return False
        return True

    def is_only_city_data_change(prov_data1, prov_data2):  # If this update only about the "city" data
        clause1 = prov_data1[prov]['confirmedCount'] == prov_data2[prov]['confirmedCount']
        clause2 = prov_data1[prov]['suspectedCount'] == prov_data1[prov]['suspectedCount']
        clause3 = prov_data1[prov]['deadCount'] == prov_data1[prov]['deadCount']
        clause4 = prov_data1[prov]['curedCount'] == prov_data1[prov]['curedCount']
        clause5 = not prov_data1[prov]['cities'] == prov_data2[prov]['cities']
        if clause1 and clause2 and clause3 and clause4 and clause5:
            return True
        return False

    province_data = {}
    modify_map = {}
    for province in json_data:
        pv_name = province['provinceName']
        province_data[pv_name] = province

    # Generate modify map
    if len(last_province_data) == 0:
        for prov in province_names:
            last_province_data[prov] = province_data[prov]
            modify_map[prov] = True
    else:
        for prov in province_names:
            if comp_prov_data(last_province_data[prov], province_data[prov]):
                modify_map[prov] = False
            else:
                modify_map[prov] = True
                last_province_data[prov] = province_data[prov]

    now_time = time.time()

    # Logic here: There are only 2 options, insert or replace.
    for prov in province_names:

        # print(province_data[prov])
        infected = province_data[prov]['confirmedCount']
        sceptical = province_data[prov]['suspectedCount']
        death = province_data[prov]['deadCount']
        cured = province_data[prov]['curedCount']
        city_data = str(province_data[prov]['cities']).replace("'", '`')

        data = (now_time, prov, infected, death, sceptical, cured, city_data)
        data_str = str(data)

        exist_same_data, val = db.query_in_column('data_record_province', 'city_data',
                                                  'province_name=%s '
                                                  'and infected=%s '
                                                  'and sceptical=%s '
                                                  'and death=%s '
                                                  'and cured=%s' % (
                                                      "'" + prov + "'", infected, sceptical, death, cured))
        # if is_only_city_data_change(last_province_data, province_data) and not startup_flag:
        if exist_same_data:
            city_data_fetch = val[0][0]
            if not str(city_data) == str(city_data_fetch):
                # print(str(city_data) + '\n' + str(city_data_fetch))
                db.replace_item_data('data_record_province', data_str)
                print('Province: ', prov, ' modified.')
        elif modify_map[prov]:
            db.insert_item_data('data_record_province', data_str)
            print('Province: ', prov, ' modified.')

        db.commit()


while True:
    skip_flag = False
    content = retry(api_fetch, 2, DXY_URL)
    overview = '{' + cut_string(content, 'window.getStatisticsService = {', '</script>').replace('}catch(e){}', '')
    overview_json = None

    region_stat_json = None
    region_stat = cut_string(content, '<script id="getAreaStat">', '</script>')
    region_stat = '[' + cut_string(region_stat, 'getAreaStat = [', '}catch(e)')

    try:

        overview_json = json.loads(overview)
        last_overview_data, last_time = analyze_overview_updated(overview_json)

    except json.decoder.JSONDecodeError as e:
        print('Overview data fetch error.', e.args)
    except pymysql.err.OperationalError as e:
        print('Overview data saving error. Reconnecting...', e.args)
        print('Reconnect result:', db.reconnect())

    try:
        region_stat_json = json.loads(region_stat)
        analyze_province(region_stat_json, last_time)

    except json.decoder.JSONDecodeError as e:
        print('Region data fetch error.', e.args)
    except pymysql.err.OperationalError as e:
        print('Region data saving error. Reconnecting...', e.args)
        print('Reconnect result:', db.reconnect())

    time.sleep(SLEEP_DELAY)

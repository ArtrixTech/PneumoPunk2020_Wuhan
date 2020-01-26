import json
import time

from utils.api import *
from utils.api_list import *
from utils.cut_string import cut_string
from utils.database import DatabaseOperation
from utils.exception_retry import retry

db = DatabaseOperation("mysql.artrix.tech", "pneu2020", "pneu",
                       "pneu2020", charset='utf8', port=33069)

last_time = None
last_overview_data = ()
SLEEP_DELAY = 5  # Unit: second


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

        data = (modify_time, region, infected, death, sceptical, cured, image_url)
        data_str = str(data)

        try:
            if not data_equal(data[1:], last_overview_data[1:]):
                db.insert_item_data('data_record', data_str)
        except TypeError:
            print('Line1: ', data, '\n Line2:', last_overview_data)

        return data, modify_time
    return None, modify_time


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

    for prov in modify_map:
        if modify_map[prov]:
            print('Province: ', prov, ' modified.')
            infected = province_data[prov]['confirmedCount']
            sceptical = province_data[prov]['suspectedCount']
            death = province_data[prov]['deadCount']
            cured = province_data[prov]['curedCount']
            city_data = str(province_data[prov]['cities']).replace("'", '`')

            data = (modify_time, prov, infected, sceptical, death, cured, city_data)
            data_str = str(data)
            db.insert_item_data('data_record_province', data_str)
            db.commit()


while True:
    skip_flag = False
    content = retry(api_fetch, 2, DXY_URL)
    overview = '{' + cut_string(content, 'window.getStatisticsService = {', '}') + '}'
    overview_json = None

    region_stat_json = None
    region_stat = cut_string(content, '<script id="getAreaStat">', '</script>')
    region_stat = '[' + cut_string(region_stat, 'getAreaStat = [', '}catch(e)')

    try:
        overview_json = json.loads(overview)
        last_overview_data, last_time = analyze_overview(overview_json)

    except json.decoder.JSONDecodeError as e:
        print('Overview data fetch error.')

    try:
        region_stat_json = json.loads(region_stat)
        analyze_province(region_stat_json, last_time)

    except json.decoder.JSONDecodeError as e:
        print('Region data fetch error.')

    time.sleep(SLEEP_DELAY)

import warnings

from utils.database import CSGODatabase
from utils.item_class import *
from utils.log import Log
from utils.specs import *

warnings.filterwarnings("ignore")

db = CSGODatabase("mysql.artrix.tech", "csgo", "csgo",
                  "CSGO", charset='utf8', port=33060)
logger = Log('Item-Refresh')


def get_max_page(price_range_i):
    try:

        content = requests.get(
            api_concat(api_list.BUFF_ITEM_API,
                       1000,
                       str(price_range_i[0]),
                       str(price_range_i[1])),
            cookies=COOKIES, headers=HEADERS).text

        jsonified = json.loads(content)

        if jsonified['code'] == 'OK':
            return jsonified['data']['total_page']
        raise ValueError('Buff returned:' + content)

    except KeyError as e:
        logger.log(str(e.args))
        logger.finished()
    except Exception as e:
        logger.log(str(e.args))
        logger.finished()


def refresh_items():
    price_range = [15, 3000]
    max_page = get_max_page(price_range)
    logger.log('Start to refresh items')
    logger.log('Total: ' + str(max_page) + ' pages.')

    for i in range(1, max_page):

        url = api_concat(api_list.BUFF_ITEM_API, i,
                         price_range[0], price_range[1])
        request = requests.get(url, headers=HEADERS, cookies=COOKIES)
        request.encoding = 'utf-8'
        content = request.text

        jsonified = json.loads(content)

        if jsonified['code'] == 'OK':
            items = jsonified['data']['items']

            for item in items:
                buff_id = item['id']
                query_result = db.query_weapon_metadata(buff_id)
                if not query_result[0]:

                    def gen_metadata_obj(buff_id_i, in_retry=False):
                        try:
                            return WeaponMetadata(buff_id, db)
                        except ValueError:
                            if not in_retry:
                                time.sleep(5)
                                return gen_metadata_obj(buff_id_i, in_retry=True)
                            return False

                    # TODO: Add API Pool system
                    metadata_obj = gen_metadata_obj(buff_id)
                    time.sleep(0.5)

                    if metadata_obj:
                        db.insert_item_meta_data(metadata_obj)
                        logger.log('Inserted item ' + metadata_obj.item_name)
                        logger.finished()
                    else:
                        logger.log('[Warning] Failed to fetch id %d' % buff_id)
                        logger.finished()
                else:
                    logger.log('Exist item %s' % query_result[1][0][0])
                    logger.finished()

        else:
            logger.log('[Warning] Failed to fetch page %d' % i)

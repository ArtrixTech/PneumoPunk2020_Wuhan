import time
from warnings import filterwarnings

import pymysql

from utils.item_class import is_metadata_obj

filterwarnings('ignore', category=pymysql.Warning)


def is_csgo_db_obj(obj):
    return isinstance(obj, CSGODatabase)


class DatabaseOperation:

    def gen_db_connction(self):
        return pymysql.connect(self._host, self._usr_name, self._password, self._db_name, charset=self._charset,
                               port=self._port)

    def __init__(self, host, usr_name, password, db_name, charset='utf8', port=3306):

        self._host = host
        self._usr_name = usr_name
        self._password = password
        self._db_name = db_name
        self._charset = charset
        self._port = port

        try:
            self.db = self.gen_db_connction()
            self.cursor = self.db.cursor()
            self.connected = True
            self._connection_parameter = [
                host, usr_name, password, db_name, charset, port]
        except pymysql.err.OperationalError as e:
            self.connected = False
            print('MySQL connection error. Info: ', e)

    def __del__(self):
        self.db.close()

    def create_item_table(self, name):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS %s ("
                            "update_time INT,"
                            "buff_id INT,"
                            "exhibition_image TEXT,"
                            "buff_trade_history JSON,"
                            "buff_selling_duration FLOAT,"
                            "buff_buy_price FLOAT,"
                            "buff_history_trade_price_median FLOAT,"
                            "buff_history_trade_price_std_error FLOAT,"
                            "steam_buy_price FLOAT,"
                            "buff_in_stock_count INT,"
                            "steam_market_url TEXT"
                            ")" % str(name))

    def insert_item_data(self, item_name, data):
        print("INSERT INTO %s VALUES %s" %
              (str(item_name), str(data)))
        self.cursor.execute("INSERT INTO %s VALUES %s" %
                            (str(item_name), str(data)))
        self.commit()

    def commit(self):
        self.db.commit()

    def execute(self, sql):
        try:
            return bool(self.cursor.execute(sql)), self.cursor.fetchall()
        except pymysql.err.OperationalError:
            try:
                self.db = self.gen_db_connction()
                self.cursor = self.db.cursor()
                self.connected = True
                return bool(self.cursor.execute(sql)), self.cursor.fetchall()
            except pymysql.err.OperationalError as e:
                self.connected = False
                print('MySQL connection error. Info: ', e)
                return False, None

    def query_in_column(self, item_value, column_name, table_name):
        return bool(self.cursor.execute("SELECT * FROM CSGO.%s WHERE %s=%s;" %
                                        (table_name, column_name, item_value))), \
               self.cursor.fetchall()

    def query_whole_column(self, column_name, table_name, where_clause=None):
        if not where_clause:
            return bool(self.cursor.execute("SELECT %s FROM CSGO.%s;" % (column_name, table_name))), \
                   self.cursor.fetchall()
        else:
            return bool(
                self.cursor.execute("SELECT %s FROM CSGO.%s WHERE %s;" % (column_name, table_name, where_clause))), \
                   self.cursor.fetchall()

    # TODO: Move this function to its right place
    def execute_with_json_return(self, sql):
        import json
        assert isinstance(sql, CSGOSql)

        keys = str(sql.select_param[0]).split(',')

        flag, result = self.execute(str(sql))

        if flag:
            rt_list = {'code': 0, 'count': len(result), 'msg': "", 'data': []}
            for item in result:

                item_dict = {}
                index = 0
                for data in item:
                    item_dict[keys[index].replace(" ", "")] = data
                    index += 1

                rt_list['data'].append(item_dict)
            return json.dumps(rt_list)
        return {'code': 400, 'count': 0, 'msg': "Database Error."}


class CSGODatabase:

    def __init__(self, host, usr_name, password, db_name, charset='utf8', port=3306):
        self.db = DatabaseOperation(
            host, usr_name, password, db_name, charset, port)

    def get_all_weapon_id(self):
        flag, result = self.db.query_whole_column(
            'buff_id', 'weapon_meta_data')
        if flag:
            rt_list = []
            for item in result:
                rt_list.append(item[0])
            return rt_list
        return False

    def get_outdated_weapon_id(self, delta_time_limit):
        """
        Query a list of outdated and to-update weapon ids.
        :param delta_time_limit: If delta_time_limit > (Now Time - Last Update Time) will the item be included.
        :return: id list
        """
        latest_time = time.time() - delta_time_limit
        flag, result = self.db.query_whole_column(
            'buff_id', 'realtime_data', 'update_time <= %s' % str(latest_time))
        if flag:
            rt_list = []
            for item in result:
                rt_list.append(item[0])
            return rt_list
        return False

    def query_weapon_metadata(self, buff_id):
        """
        Query if one weapon is existed in the metadata table.
        :param buff_id: Buff ID
        :return: Weapon detailed data
        """
        return self.db.query_in_column(buff_id, 'buff_id', 'weapon_meta_data')

    # TODO: Add update module.
    def insert_item_meta_data(self, weapon_metadata):
        """
        Add or modify new-item data -> table meta_data .
        :param weapon_metadata: metadata through class WeaponMetadata
        :return:
        """
        assert is_metadata_obj(weapon_metadata)
        self.db.cursor.execute("INSERT IGNORE INTO weapon_meta_data "
                               "VALUES %s " % str(weapon_metadata.sql_values()))
        self.db.commit()

    def create_item_table_if_not_exist(self, buff_id):
        self.db.cursor.execute("CREATE TABLE IF NOT EXISTS `%s` ("
                               "name TEXT,"
                               "buff_id INT,"
                               "update_time INT,"
                               "buff_trade_history TEXT,"
                               "buff_selling_duration FLOAT,"
                               "buff_buy_price FLOAT,"
                               "buff_history_trade_price_median FLOAT,"
                               "buff_history_trade_price_std_error FLOAT,"
                               "steam_buy_price FLOAT,"
                               "buff_in_stock_count INT"
                               ")" % str(buff_id))

    def update_item_data(self, buff_id, data):
        self.db.cursor.execute(
            "REPLACE INTO `realtime_data` VALUES %s" % str(data))
        self.db.commit()

    def insert_item_record(self, buff_id, data):
        self.db.cursor.execute(
            "INSERT INTO `%s` VALUES %s" % (str(buff_id).replace("'", "`"), str(data)))
        self.db.commit()

    def query_realtime_data(self, buff_id, data_name):
        to_execute = "SELECT %s FROM `realtime_data` WHERE buff_id = %s;" % (
            str(data_name), str(buff_id).replace("'", "`"))
        return bool(self.db.cursor.execute(to_execute)), self.db.cursor.fetchall()


class CSGOSql:

    def __init__(self):
        self.sql = ""

        # TODO: Edit param part
        self.select_param = []
        self._limit_param = []
        self._order_param = []
        self._where_param = []

    def __str__(self):
        return self.sql

    def _end(self):
        self.sql += ' '
        return self

    def select(self, content, source):
        self.sql += 'select %s from %s' % (str(content), str(source))
        self.select_param.append(content)
        self.select_param.append(source)
        return self._end()

    def where(self, condition):
        self.sql += 'where %s' % str(condition)
        return self._end()

    def order(self, by_column_name, order='desc'):
        self.sql += 'order by %s %s' % (str(by_column_name), str(order))
        return self._end()

    def limit(self, num):
        self.sql += 'limit %s' % str(num)
        return self._end()

    def limit_between(self, start, length):
        self.sql += 'limit %s ,%s' % (str(start), str(length))
        return self._end()

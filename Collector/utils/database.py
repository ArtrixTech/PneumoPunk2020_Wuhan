from warnings import filterwarnings

import pymysql

filterwarnings('ignore', category=pymysql.Warning)


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

    def insert_item_data(self, item_name, data):
        print("INSERT INTO %s VALUES %s" %
              (str(item_name), str(data)))
        self.cursor.execute("INSERT IGNORE INTO %s VALUES %s" %
                            (str(item_name), str(data)))
        self.commit()

    def replace_item_data(self, item_name, data):
        print("REPLACE INTO %s VALUES %s" %
              (str(item_name), str(data)))
        self.cursor.execute("REPLACE INTO %s VALUES %s" %
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

    def query_in_column(self, table_name, select_clause, where_clause):
        return bool(self.cursor.execute("SELECT %s FROM pneu2020.%s WHERE %s;" %
                                        (select_clause, table_name, where_clause))), \
               self.cursor.fetchall()

    def query_whole_column(self, column_name, table_name, where_clause=None):
        if not where_clause:
            return bool(self.cursor.execute("SELECT %s FROM CSGO.%s;" % (column_name, table_name))), \
                   self.cursor.fetchall()
        else:
            return bool(
                self.cursor.execute("SELECT %s FROM CSGO.%s WHERE %s;" % (column_name, table_name, where_clause))), \
                   self.cursor.fetchall()

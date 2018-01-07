import MySQLdb


class EdgeDB(object):

    def __init__(self):
        self.get_conn()


    def get_conn(self):
        try:
            self.conn = MySQLdb.connect(
                host='127.0.0.1',
                db='edgewell',
                user='root',
                passwd='1234',
                port=3306,
                charset='utf8'
            )
        except Exception as e:
            print(str(e))


    def close_conn(self):
        try:
            if self.conn:
                self.conn.close()
        except Exception as e:
            print(str(e))
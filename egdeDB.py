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



    def add_one_store(self,store_id,store_name,all_link):
        ''' 插入数据 '''
        # 受影响的行数
        row_count = 0
        try:
            sql = (
                "INSERT INTO `store`(`store_id`,`store_name`,`all_razor_link`) VALUE"
                "(%s, %s,%s);"
            )
            # 获取链接和cursor
            cursor = self.conn.cursor()
            # 执行sql
            # 提交数据到数据库
            cursor.execute(sql, (store_id,store_name,all_link))
            # cursor.execute(sql, ('标题12', '/static/img/news/01.png', '新闻内容6', '推荐', 1))
            # 提交事务
            self.conn.commit()
        except Exception as e:
            print(str(e))
            # 回滚事务
            self.conn.rollback()
            cursor.close()
            self.close_conn()

        row_count = cursor.rowcount
        # row_count > 0 表示成功
        return row_count > 0



    def close_conn(self):
        try:
            if self.conn:
                self.conn.close()
        except Exception as e:
            print(str(e))




if __name__ == '__main__':
    stores = [['3166565419','Schick官方旗舰店',r'https://schick.tmall.com/search.htm?spm=a1z10.1-b-s.w5002-16126242899.1.1707740GVK5dF&search=y'],
              ['925649214','Gillette官方旗舰店',r'https://gillette.tmall.com/category.htm?spm=a1z10.1-b-s.w14208996-16789983496.3.76a5b9d3UiPRPe&search=y&scene=taobao_shop'],
              ['2958888567','SchickLRMX专卖店','https://schicklrmx.tmall.com/category.htm?spm=a1z10.3-b-s.w5001-15876109104.6.660358a0XGzpyd&search=y&scene=taobao_shop'],
              ['1658892141','Apache官方旗舰店','https://apachejj.tmall.com/search.htm?spm=a1z10.4-b-s.w5001-14450093363.5.338cb0eckZBWZd&search=y&scene=taobao_shop']
              ]

    edge = EdgeDB()
    for store in stores:
        edge.add_one_store(store[0],store[1],store[2])
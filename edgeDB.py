import MySQLdb
from datetime import datetime


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


    def get_one_store(self,store_id):
        try:
            sql = '''SELECT store_id,store_name,all_razor_link FROM store
                     WHERE store_id = {} 
            '''.format(store_id)
            cursor = self.conn.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            cursor.close()
            return row
        except Exception as e:
            cursor.close()
            print(str(e))


    def get_stores(self):
        try:
            sql = '''SELECT store_id,store_name,all_razor_link FROM store
            '''
            cursor = self.conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except Exception as e:
            cursor.close()
            print(str(e))


    def add_one_razor(self,razor_dict):
        cursor = self.conn.cursor()
        try:
            sql = """
              INSERT INTO razor (razor_id,razor_spu_name,razor_spu_link,scrapy_date,seller_id)
              VALUES (%s,%s,%s,%s,%s)
              ON DUPLICATE KEY UPDATE razor_spu_name = VALUES (razor_spu_name),razor_spu_link = VALUES (razor_spu_link),scrapy_date = VALUES(scrapy_date)
            """
            cursor.execute(sql,(razor_dict['razor_id'],razor_dict['name'],razor_dict['link'],razor_dict['date'],razor_dict['store_id']))
            self.conn.commit()
        except Exception as e:
            print(str(e))
        cursor.close()



    def add_one_sku(self,row):
        try:
            cursor = self.conn.cursor()
            sql= """
                    INSERT INTO sku_detail (sku_id,sku_name,sku_sub_title,discount_content,qty_sold,comm_num,stock_nums,add_favorites,razor_code,spu_id,
                    price,promo_price,scrapy_date)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            cursor.execute(sql,row)
            self.conn.commit()
        except Exception as e:
            print(str(e))




    def close_conn(self):
        try:
            if self.conn:
                self.conn.close()
        except Exception as e:
            print(str(e))




if __name__ == '__main__':
    edge = EdgeDB()
    razor_dict = {}
    razor_dict['razor_id'] = '546001254320'
    razor_dict['name'] = 'Schick/舒适手动剃须刀超巧男士便携轻便刀1刀架1刀片2刀头'
    razor_dict['link'] = '//detail.tmall.com/item.htm?id=546001254320&rn=a19ca4077bd75cffa52f70f12ecff10f&abbucket=7'
    razor_dict['store_id'] = '3166565419'
    razor_dict['date'] = datetime.now().date()

    edge.add_one_razor(razor_dict)


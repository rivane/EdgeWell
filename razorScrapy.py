from selenium import  webdriver
import time
from scrapy import Selector
import MySQLdb
import re
import pandas as pd
from datetime import datetime

from commons import extract_num
from edgeDB import EdgeDB


RAZOR_SEARCH = 'https://detail.tmall.com/item.htm?spm=a1z10.3-b-s.w4011-16789972104.90.14f0e970bqo7tl&id={0}'


class RazorScrapy:
    def __init__(self):
        self.db = EdgeDB()
        self.browser = webdriver.Chrome(executable_path='chromedriver.exe')
        self.account = '傲磊烁烁'
        self.passwd = 'baoaolei1989'


    def login_Tmall(self):
        login_url = 'https://login.tmall.com/'
        self.browser.get(login_url)
        self.browser.switch_to.frame(0)
        time.sleep(20)
        self.browser.find_element_by_css_selector('.quick-form .login-links a').click()
        self.browser.find_element_by_css_selector('#TPL_username_1').send_keys(self.account)
        self.browser.find_element_by_css_selector('#TPL_password_1').send_keys(self.passwd)

        self.browser.find_element_by_css_selector('#J_SubmitStatic').click()



    def getAllRazorLinks(self,store_id):
        store_razor_link = self.db.get_one_store(store_id)[-1]
        self.browser.get(store_razor_link)
        time.sleep(5)
        t_selector = Selector(text=self.browser.page_source)
        item5lines = t_selector.css('.J_TItems .item5line1')

        for item5line in item5lines:
            items = item5line.css('.item .detail')
            for item in items:
                razor_dict = {}
                razor_link =  item.css('a ::attr(href)').extract_first('')
                razor_name = item.css('a ::text').extract_first()
                razor_id = 'null'
                mbj = re.match('.*?id=(\d+).*',razor_link)
                if mbj:
                    razor_id = mbj.group(1)
                razor_dict['razor_id'] = razor_id
                razor_dict['name'] = razor_name
                razor_dict['link'] = razor_link
                razor_dict['store_id'] = store_id
                razor_dict['date'] = datetime.now().date()

                self.db.add_one_razor(razor_dict)




    def getSKUDetail(self,id):
        # get the detail link of the product, return the detail link
        searched_url = RAZOR_SEARCH.format(id)
        self.browser.get(searched_url)
        time.sleep(15)
        skus = self.browser.find_elements_by_css_selector('.tb-sku ul li a')
        if skus:
            for sku in skus:
                if sku.text:
                    sku.click()
                    time.sleep(3)
                    current_url = self.browser.current_url
                    sku_name = sku.text
                    mbj = re.match('.*?skuId=(\d+).*', current_url)
                    if mbj:
                        sku_id = mbj.group(1)
                    t_selector = Selector(text=self.browser.page_source)
                    sku_sub_title = t_selector.css('.tb-detail-hd .newp::text').extract_first('').strip()

                    discount_content = t_selector.css('.tm-shopPromo-panel .tm-shopPromotion-title dd::text').extract_first(" ")
                    qty_sold = int(t_selector.css('.tm-ind-panel .tm-ind-sellCount .tm-count::text').extract_first(0))
                    price =  float(t_selector.css('.tm-price-panel .tm-price::text').extract_first(0))
                    promo_price = float(t_selector.css('.tm-promo-panel .tm-price::text').extract_first(0))
                    comm_num = int(t_selector.css('.tm-ind-panel .tm-ind-reviewCount .tm-count::text').extract_first(0))
                    stock_nums = t_selector.css('#J_EmStock ::text').extract_first('')
                    stock_nums = extract_num(stock_nums)
                    add_favorites = t_selector.css('#J_CollectCount ::text').extract_first('0')
                    add_favorites = extract_num(add_favorites)
                    razor_codes = t_selector.css('#J_AttrUL li::text').extract()
                    for rc in razor_codes:
                        if '号' in rc:
                            razor_code = rc[3:].strip()

                    row = (sku_id,sku_name,sku_sub_title,discount_content,qty_sold,comm_num,stock_nums,add_favorites,razor_code,id
                                                      ,price,promo_price,datetime.now().date())
                    self.db.add_one_sku(row)
            else:
                current_url = self.browser.current_url
                t_selector = Selector(text=self.browser.page_source)
                sku_name = t_selector.css('.tb-detail-hd h1::text').extract_first('').strip()
                mbj = re.match('.*?skuId=(\d+).*', current_url)
                if mbj:
                    sku_id = mbj.group(1)
                else:
                    sku_id = id
                sku_sub_title = t_selector.css('.tb-detail-hd .newp::text').extract_first(' ').strip()

                discount_content = t_selector.css('.tm-shopPromo-panel .tm-shopPromotion-title dd::text').extract_first('0')
                qty_sold = int(t_selector.css('.tm-ind-panel .tm-ind-sellCount .tm-count::text').extract_first(0))
                price = float(t_selector.css('.tm-price-panel .tm-price::text').extract_first(0))
                promo_price = float(t_selector.css('.tm-promo-panel .tm-price::text').extract_first(0))
                comm_num = int(t_selector.css('.tm-ind-panel .tm-ind-reviewCount .tm-count::text').extract_first(0))
                stock_nums = t_selector.css('#J_EmStock ::text').extract_first(' ')
                stock_nums = extract_num(stock_nums)
                add_favorites = t_selector.css('#J_CollectCount ::text').extract_first(' ')
                add_favorites = extract_num(add_favorites)
                try:
                    razor_codes = t_selector.css('#J_AttrUL li::text').extract()
                    for rc in razor_codes:
                        if '号' in rc:
                            razor_code = rc[3:].strip()
                except:
                    razor_code = ''

                row = (
                sku_id, sku_name, sku_sub_title, discount_content, qty_sold, comm_num, stock_nums, add_favorites, razor_code, id
                , price, promo_price, datetime.now().date())
                self.db.add_one_sku(row)





    def getRazordetail(self):
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT razor_id FROM razor')
        spu_ids = cursor.fetchall()
        cursor.execute('SELECT spu_id FROM sku_detail')
        searched = [r[0] for r in cursor.fetchall()]
        for id in spu_ids:
            if id[0] in searched:
                continue
            self.getSKUDetail(id[0])




    # def getComments(self,spu_id,seller_id):
    #     comments_url = 'https://rate.tmall.com/list_detail_rate.htm?itemId={0}&sellerId={1}&order=3&currentPage={2}'
    #     i = 0
    #     self.browser.get(comments_url.format(spu_id, seller_id, i))
    #     try:
    #         data = self.browser.page_source
    #         data = re.findall('<body>(.*?)</body>', data)[0]
    #         data = '{' + data + '}'
    #         df = pd.read_json(data)
    #         page = df.ix['paginator', 'rateDetail']['lastPage']
    #
    #         while i <= page:
    #             self.browser.get(comments_url.format(spu_id, seller_id, i))
    #             data = self.browser.page_source
    #             data = re.findall('<body>(.*?)</body>', data)[0]
    #             data = '{' + data + '}'
    #             df = pd.read_json(data)
    #             rows = df.ix['rateList', 'rateDetail']
    #             for row in rows:
    #                 insert_sql = """
    #                        INSERT INTO comments(spu_id,seller_id,tmall_id,content)
    #                        VALUES (%s,%s,%s,%s)
    #                        """
    #                 data = (spu_id,seller_id,row['displayUserNick'], row['rateContent'])
    #                 self.cursor.execute(insert_sql, data)
    #                 self.conn.commit()
    #             i += 1
    #             time.sleep(20)
    #     except Exception as e:
    #         print(str(e))
    #         return None




    def __del__(self):
        self.db.close_conn()








if __name__ == '__main__':
    rs = RazorScrapy()
    rs.login_Tmall()
    all_stores = rs.db.get_stores()
    for store in all_stores:
        rs.getAllRazorLinks(store[0])

    print('get razor done')

    rs.getRazordetail()

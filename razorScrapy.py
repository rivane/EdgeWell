from selenium import  webdriver
import time
from scrapy import Selector
import MySQLdb
import re
import pandas as pd
from datetime import datetime

from commons import extract_num
import settings


GILLETTE_RAZROS = r'https://gillette.tmall.com/category.htm?spm=a1z10.1-b-s.w14208996-16789983496.3.76a5b9d3UiPRPe&search=y&scene=taobao_shop'
SCHICK_RAZORS =r'https://schick.tmall.com/search.htm?spm=a1z10.1-b-s.w5002-16126242899.1.1707740GVK5dF&search=y'
RAZOR_SEARCH = 'https://detail.tmall.com/item.htm?spm=a1z10.3-b-s.w4011-16789972104.90.14f0e970bqo7tl&id={0}'


class RazorScrapy:
    def __init__(self):
        self.browser = webdriver.Chrome(executable_path=settings.CHROME_DIR_PATH)
        self.conn = MySQLdb.connect(settings.HOST, settings.DB_UESR, settings.DB_PASSWD, settings.DB_NAME, charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()
        self.account = settings.USER
        self.passwd = settings.PASSWORD


    def login_Tmall(self):
        login_url = 'https://login.tmall.com/'
        self.browser.get(login_url)
        self.browser.switch_to.frame(0)
        time.sleep(20)
        self.browser.find_element_by_css_selector('.quick-form .login-links a').click()
        self.browser.find_element_by_css_selector('#TPL_username_1').send_keys(self.account)
        self.browser.find_element_by_css_selector('#TPL_password_1').send_keys(self.passwd)

        self.browser.find_element_by_css_selector('#J_SubmitStatic').click()



    def getAllRazorLinks(self,store_link = SCHICK_RAZORS ):
        self.browser.get(store_link)
        time.sleep(5)
        t_selector = Selector(text=self.browser.page_source)
        item5lines = t_selector.css('.J_TItems .item5line1')

        for item5line in item5lines:
            items = item5line.css('.item .detail')
            for item in items:
                razor_link =  item.css('a ::attr(href)').extract_first('')
                razor_name = item.css('a ::text').extract_first()
                mbj = re.match('.*?id=(\d+).*',razor_link)
                if mbj:
                    razor_id = mbj.group(1)

                self.cursor.execute("""
                INSERT INTO razor (razor_id,razor_spu_name,razor_spu_link)
                VALUES (%s,%s,%s)
                ON DUPLICATE KEY UPDATE razor_spu_name = VALUES (razor_spu_name),razor_spu_link = VALUES (razor_spu_link)
                """,(razor_id,razor_name,razor_link))
                self.conn.commit()


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

                    sqlStatement = """
                    INSERT INTO sku_detail (sku_id,sku_name,sku_sub_title,discount_content,qty_sold,comm_num,stock_nums,add_favorites,razor_code,spu_id,
                    price,promo_price)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE discount_content = VALUES (discount_content)
                    """
                    self.cursor.execute(sqlStatement,(sku_id,sku_name,sku_sub_title,discount_content,qty_sold,comm_num,stock_nums,add_favorites,razor_code,id
                                                      ,price,promo_price))
                    self.conn.commit()
                    print((sku_id,sku_name,sku_sub_title,discount_content,qty_sold,comm_num,stock_nums,add_favorites,razor_code,id
                                                      ,price,promo_price))
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

                sqlStatement = """
                                    INSERT INTO sku_detail (sku_id,sku_name,sku_sub_title,discount_content,qty_sold,comm_num,stock_nums,add_favorites,razor_code,spu_id,
                                    price,promo_price)
                                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                    """
                print((sku_id, sku_name, sku_sub_title, discount_content, qty_sold, comm_num, stock_nums, add_favorites,
                       razor_code, id
                       , price, promo_price))
                self.cursor.execute(sqlStatement, (
                sku_id, sku_name, sku_sub_title, discount_content, qty_sold, comm_num, stock_nums, add_favorites,
                razor_code, id
                , price, promo_price))
                self.conn.commit()




    def getRazordetail(self):
        self.cursor.execute('SELECT razor_id FROM razor')
        spu_ids = self.cursor.fetchall()
        self.cursor.execute('SELECT spu_id FROM sku_detail')
        searched = [r[0] for r in self.cursor.fetchall()]
        for id in spu_ids:
            if id[0] in searched:
                continue
            self.getSKUDetail(id[0])




    def getComments(self,spu_id,seller_id):
        comments_url = 'https://rate.tmall.com/list_detail_rate.htm?itemId={0}&sellerId={1}&order=3&currentPage={2}'
        i = 0
        self.browser.get(comments_url.format(spu_id, seller_id, i))
        try:
            data = self.browser.page_source
            data = re.findall('<body>(.*?)</body>', data)[0]
            data = '{' + data + '}'
            df = pd.read_json(data)
            page = df.ix['paginator', 'rateDetail']['lastPage']

            while i <= page:
                self.browser.get(comments_url.format(spu_id, seller_id, i))
                data = self.browser.page_source
                data = re.findall('<body>(.*?)</body>', data)[0]
                data = '{' + data + '}'
                df = pd.read_json(data)
                rows = df.ix['rateList', 'rateDetail']
                for row in rows:
                    insert_sql = """
                           INSERT INTO comments(spu_id,seller_id,tmall_id,content)
                           VALUES (%s,%s,%s,%s)
                           """
                    data = (spu_id,seller_id,row['displayUserNick'], row['rateContent'])
                    self.cursor.execute(insert_sql, data)
                    self.conn.commit()
                i += 1
                time.sleep(20)
        except Exception as e:
            print(str(e))
            return None




    def __del__(self):
        self.conn.close()








if __name__ == '__main__':
    rs = RazorScrapy()
    rs.login_Tmall()
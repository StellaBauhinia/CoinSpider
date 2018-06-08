import re
import json
from datetime import datetime, tzinfo, timezone
import pytz
import requests
import logging
import pymongo
from scrapy.conf import settings
from scrapy import Spider, Selector
from scrapy.http import Request
from CoinSpider.items import *

class CoinSpider(Spider):
    name = 'CoinDetailSpider'
    allowed_domains = ['feixiaohao.com']
    start_urls = [
        #'http://www.feixiaohao.com/all/'
    ]
    client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
    db = client[settings['MONGO_DB']]
    url_coll = db[settings['MONGO_COLL1']]
    for sub_url in url_coll.find({}):
        start_urls.append('http://www.feixiaohao.com'+sub_url['url'])

    logging.getLogger("requests").setLevel(logging.WARNING)  # 将requests的日志级别设成WARNING

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_coin)
            
    def parse_coin(self,response):
        selector = Selector(response)

        coin = CoinItem()
        # description
        desc = selector.xpath('//div[@class="des"]/a').extract()
        description = re.findall(r'<a href="(.*?)" target="_blank">', str(desc), re.S)
        if len(description) is not 0:
            base_url='http://www.feixiaohao.com'
            desc_url = base_url + description[0]
            #print(desc_url)
            response = requests.get(desc_url)
            desc_selector = Selector(response)
            desc_content = desc_selector.xpath('//div[@class="boxContain"]/div/p[2]').extract()
            desc_content_no_tag = re.findall(r'<p>(.*?)</p>', str(desc_content), re.S)
            coin['description'] = ''.join(i.strip() for i in desc_content_no_tag)
            #print(coin['description'])

        # market
        market = selector.xpath('//div[@id="baseInfo"]/div[@class="firstPart"]/div/div[@class="value"]').extract()
        values = []
        for value in market:
            market_value = re.findall(r'<div class="value">(.*?)<', value, re.S)
            values.append(market_value[0])

        if len(values) is not 0:
            coin['market_capitalization'] = values[0]
            coin['market_count'] = values[1]
            coin['publish_count'] = values[2]
            coin['tx_count'] = values[3]
            coin['time'] = int(round(datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()))
            #print(coin['market_capitalization'], ' ', coin['market_count'], ' ', coin['publish_count'], ' ', coin['tx_count'])

         # base info
        items = selector.xpath('//div[@id="baseInfo"]/div[@class="secondPark"]/ul/li').extract()
        for item in items:
            base_info = re.findall(r'<li>.*?<span class="tit">(.*?)</span>.*?<span class="value">(.*?)</span>.*?</li>', item, re.S)
            if len(base_info) is not 0:
                if base_info[0][0] == '英文名：':
                    coin['english_name'] = base_info[0][1].strip()
                    coin['code'] = coin['english_name'][coin['english_name'].find('/')+1:]
                    #print(coin['english_name'])
                elif base_info[0][0] == '中文名：':
                    coin['chinese_name'] = base_info[0][1].strip()
                    #print(coin['chinese_name'])
                elif base_info[0][0] == '上架交易所：':
                    e_count=re.findall(r'<a href="#tickerlist">(.*?)</a>', str(base_info[0][1].strip()))
                    coin['exchanger_count'] = re.sub("[^0-9]", "", e_count[0])
                    #print(coin['exchanger_count'])
                elif base_info[0][0] == '发行时间：':
                    coin['publish_time'] = base_info[0][1].strip()
                    #print(coin['publish_time'])
                elif base_info[0][0] == '白皮书：':
                    paper_link=str(base_info[0][1].strip())
                    if  paper_link != '－':
                        paper_link=re.findall(r'<a href="(.*?)" target=', paper_link)[0]
                        if paper_link.find('http://') != -1:
                            paper_link=paper_link[paper_link.find('http:')+5 :]
                    coin['white_paper'] = paper_link
                    #print(coin['white_paper'])
                elif base_info[0][0] == '网站：':
                    websites = re.findall(r'<a href="(.*?)" rel="nofollow" target="_blank">', base_info[0][1], re.S)

                    if len(websites) is not 0:
                        office_websites = []
                        for website in websites:
                            if website.find('http://') != -1:
                                website=website[website.find('http:')+5 :]
                            office_websites.append(website.strip())
                        coin['website'] = office_websites
                        #print(coin['website'])
                elif base_info[0][0] == '区块站：':
                    explorers = []
                    block_explorers = re.findall(r'<a href="(.*?)" rel="nofollow" target="_blank">', base_info[0][1], re.S)
                    if block_explorers is not []:
                        for block_explorer in block_explorers:
                            if block_explorer.find('http://') != -1:
                                block_explorer=block_explorer[block_explorer.find('http:')+5 :]
                            explorers.append(block_explorer.strip())
                        coin['block_explorer'] = explorers
                        #print(coin['block_explorer'])
                elif base_info[0][0] == '是否代币：':
                    coin['is_token'] = base_info[0][1].strip()
                    #print(coin['is_token'])
                elif base_info[0][0] == '众筹价格：':
                    ico_price = re.findall(r'<a href="#ico">(.*?)</a>', base_info[0][1], re.S)
                    coin['ico_price'] = ico_price[0].strip()
                    #print(coin['ico_price'])
        yield coin

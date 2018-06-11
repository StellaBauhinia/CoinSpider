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
import urllib.parse

class CoinDetailSpider(Spider):
    name = 'CoinDetailSpider'
    allowed_domains = ['feixiaohao.com']
    custom_settings = {
        'LOG_LEVEL':'INFO'
    }
    start_urls = [
        #'http://www.feixiaohao.com/all/'
    ]
    username = urllib.parse.quote_plus(settings['MONGO_USER'])
    password = urllib.parse.quote_plus(settings['MONGO_PASS'])
    client = pymongo.MongoClient('mongodb://%s:%s@192.168.31.102:1507' % (username, password))
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

        coin_zh = CoinItem_zh()

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
            coin_zh['description_zh'] = ''.join(i.strip() for i in desc_content_no_tag)
            #print(coin_zh['description'])

        # market
        market = selector.xpath('//div[@id="baseInfo"]/div[@class="firstPart"]/div/div[@class="value"]').extract()
        values = []
        for value in market:
            market_value = re.findall(r'<div class="value">(.*?)<', value, re.S)
            values.append(market_value[0])

        if len(values) is not 0:
            coin_zh['market_capitalization'] = values[0]
            coin_zh['market_count'] = values[1]
            coin_zh['publish_count'] = values[2]
            coin_zh['tx_count'] = values[3]
            coin_zh['time'] = int(round(datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()))
            #print(coin_zh['market_capitalization'], ' ', coin_zh['market_count'], ' ', coin_zh['publish_count'], ' ', coin_zh['tx_count'])

         # base info
        items = selector.xpath('//div[@id="baseInfo"]/div[@class="secondPark"]/ul/li').extract()
        for item in items:
            base_info = re.findall(r'<li>.*?<span class="tit">(.*?)</span>.*?<span class="value">(.*?)</span>.*?</li>', item, re.S)
            if len(base_info) is not 0:
                if base_info[0][0] == '英文名：':
                    coin_zh['english_name'] = base_info[0][1].strip()
                    coin_zh['code'] = coin_zh['english_name'][coin_zh['english_name'].find('/')+1:]
                    #print(coin_zh['english_name'])
                elif base_info[0][0] == '中文名：':
                    coin_zh['chinese_name_zh'] = base_info[0][1].strip()
                    #print(coin_zh['chinese_name'])
                elif base_info[0][0] == '上架交易所：':
                    e_count=re.findall(r'<a href="#tickerlist">(.*?)</a>', str(base_info[0][1].strip()))
                    coin_zh['exchanger_count'] = re.sub("[^0-9]", "", e_count[0])
                    #print(coin_zh['exchanger_count'])
                elif base_info[0][0] == '发行时间：':
                    coin_zh['publish_time'] = base_info[0][1].strip()
                    #print(coin_zh['publish_time'])
                elif base_info[0][0] == '白皮书：':
                    paper_link=str(base_info[0][1].strip())
                    if  paper_link != '－':
                        paper_link=re.findall(r'<a href="(.*?)" target=', paper_link)[0]
                        if paper_link.find('http://') != -1:
                            paper_link=paper_link[paper_link.find('http:')+5 :]
                    coin_zh['white_paper'] = paper_link
                    #print(coin_zh['white_paper'])
                elif base_info[0][0] == '网站：':
                    websites = re.findall(r'<a href="(.*?)" rel="nofollow" target="_blank">', base_info[0][1], re.S)

                    if len(websites) is not 0:
                        office_websites = []
                        for website in websites:
                            if website.find('http://') != -1:
                                website=website[website.find('http:')+5 :]
                            office_websites.append(website.strip())
                        coin_zh['website'] = office_websites
                        #print(coin_zh['website'])
                elif base_info[0][0] == '区块站：':
                    explorers = []
                    block_explorers = re.findall(r'<a href="(.*?)" rel="nofollow" target="_blank">', base_info[0][1], re.S)
                    if block_explorers is not []:
                        for block_explorer in block_explorers:
                            if block_explorer.find('http://') != -1:
                                block_explorer=block_explorer[block_explorer.find('http:')+5 :]
                            explorers.append(block_explorer.strip())
                        coin_zh['block_explorer'] = explorers
                        #print(coin_zh['block_explorer'])
                elif base_info[0][0] == '是否代币：':
                    coin_zh['is_token'] = base_info[0][1].strip()
                    #print(coin_zh['is_token'])
                elif base_info[0][0] == '众筹价格：':
                    ico_price = re.findall(r'<a href="#ico">(.*?)</a>', base_info[0][1], re.S)
                    coin_zh['ico_price'] = ico_price[0].strip()
                    #print(coin_zh['ico_price'])
        yield coin_zh

import re
import json
import time
import requests
import logging
from scrapy import Spider, Selector
from scrapy.http import Request
from CoinSpider.items import *

class CoinSpider(Spider):
    name = 'CoinSpider'
    allowed_domains = ['feixiaohao.com']
    start_urls = [
        'http://www.feixiaohao.com/all/'
    ]
    logging.getLogger("requests").setLevel(logging.WARNING)  # 将requests的日志级别设成WARNING

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_coin)
            
    def parse_coin(self,response):
        selector = Selector(response)

        items = selector.xpath('//div[@class="new-main-box"]/table/tbody/tr/td/a').extract()
        for item in items:
            urlItem = CoinspiderItem()
            urls = re.findall(r'<a href="(.*?)" target="_blank">.*? alt="(.*?)">', item, re.S)
            if len(urls) > 0:
                print(urls[0][0])
                urlItem['url']=''.join(urls[0][0])
                print(urls[0][1])
                urlItem['name']=''.join(urls[0][1])
                yield urlItem

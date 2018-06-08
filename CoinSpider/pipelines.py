# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymongo
from scrapy.conf import settings
from CoinSpider.items import *

class CoinspiderPipeline(object):
    def process_item(self, item, spider):
        return item

class CoinsMongo(object):
    def __init__(self):
        self.client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        self.db = self.client[settings['MONGO_DB']]
        self.CoinspiderItem = self.db[settings['MONGO_COLL1']]
        self.CoinItem = self.db[settings['MONGO_COLL2']]

    '''def process_item(self, item, spider):
        #postItem = dict(item)
        #self.post.insert(postItem)
        if isinstance(item,CoinspiderItem):
        	try:
        		count = self.CoinspiderItem.find({'name':item['name']}).count()
        		if count > 0:
        			self.CoinspiderItem.update({'name':item['name']}.dict(item))
        		else:
        			self.CoinspiderItem.insert(dict(item))
        	except Exception as e:
        		print(e)
        return item'''
    def process_item(self, item, spider):
        """ 判断item的类型，并作相应的处理，再入数据库 """
        if isinstance(item, CoinItem):
            try:
                count = self.CoinItem.find({'english_name': item['english_name']}).count()
                if count > 0:
                    self.CoinItem.update({'english_name': item['english_name']}, dict(item))
                else:
                    self.CoinItem.insert(dict(item))
            except Exception as e:
                print(e)
                pass
        elif isinstance(item, CoinspiderItem):
            try:
                count = self.CoinspiderItem.find({'name': item['name']}).count()
                if count > 0:
                    self.CoinspiderItem.update({'name': item['name']}, dict(item))
                else:
                    self.CoinspiderItem.insert(dict(item))
            except Exception as e:
                print(e)
                pass

# 写入json文件
'''class JsonWritePipline(object):
    def __init__(self):
        #self.file = open('coinsUrl.json','w',encoding='utf-8')
        self.file = open('coinsDetails.json','w',encoding='utf-8')

    def process_item(self,item,spider):
        line  = json.dumps(dict(item),ensure_ascii=False)+"\n"
        self.file.write(line)
        return item

    def spider_closed(self,spider):
        self.file.close()'''

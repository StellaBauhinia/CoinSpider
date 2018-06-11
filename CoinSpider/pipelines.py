# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymongo
from scrapy.conf import settings
from CoinSpider.items import *
import urllib.parse
import os

checkFile = "isRunning.txt"
class CoinspiderPipeline(object):
    def process_item(self, item, spider):
        return item

class CoinsMongo(object):
    def __init__(self):
        #self.client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'],username=settings['MONGO_USER'],passowrd=settings['MONGO_PASS'])
        username = urllib.parse.quote_plus(settings['MONGO_USER'])
        password = urllib.parse.quote_plus(settings['MONGO_PASS'])
        #host = urllib.parse.quote_plus(settings['MONGO_HOST'])
        #port = urllib.parse.quote_plus(str(settings['MONGO_PORT']))
        #print(uri)
        self.client = pymongo.MongoClient('mongodb://%s:%s@192.168.31.102:1507' % (username, password))
        self.db = self.client[settings['MONGO_DB']]
        f = open(checkFile,"w")
        f.close()
        self.CoinspiderItem = self.db[settings['MONGO_COLL1']]
        self.CoinItem_zh = self.db[settings['MONGO_COLL2']]

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
        if isinstance(item, CoinItem_zh):
            try:
                count = self.CoinItem_zh.find({'english_name': item['english_name']}).count()
                if count > 0:
                    self.CoinItem_zh.update({'english_name': item['english_name']}, dict(item))
                else:
                    self.CoinItem_zh.insert(dict(item))
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

    def close_spider(self,spider):
        self.client.close()
        isFileExist = os.path.isfile(checkFile)
        if isFileExist:
            os.remove(checkFile)

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

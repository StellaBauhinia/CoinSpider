import json
import pymongo
from opencc import OpenCC
import urllib.parse
import requests
import re


username = 
password = 
client = pymongo.MongoClient('mongodb://%s:%s@192.168.31.102:1507' % (username, password))

db = 
coll_zh = db['CoinDetails_zh']
coll_hk = db['CoinDetails_hk']
url = 'https://currency-api.appspot.com/api/CNY/USD.json'
rate = requests.get(url).json()['rate']

for record in coll_zh.find({}):
    current_des = record.pop('description_zh')
    current_name =  record.pop('chinese_name_zh')
    openCC = OpenCC('s2t')
    new_des = openCC.convert(current_des)
    new_name = openCC.convert(current_name)
    record['description_hk'] = new_des
    record['chinese_name_hk'] = new_name

    if record['market_capitalization'] != '?':
        market_value = int(re.sub("[^0-9]", "", record['market_capitalization']))
        record['market_capitalization'] = '$'+str(round(float(market_value)*rate))

    if record['tx_count'] != '?':
        tx_value = int(re.sub("[^0-9]", "", record['tx_count']))
        record['tx_count'] = '$'+str(round(float(tx_value)*rate))

    count = coll_hk.find({'english_name': record['english_name']}).count()
    if count > 0:
        coll_hk.update({'english_name': record['english_name']}, record)
    else:
        coll_hk.insert(record)

    pass
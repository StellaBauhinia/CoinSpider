import json
import pymongo
from opencc import OpenCC

client = pymongo.MongoClient(host='127.0.0.1',port=27017)
db = client['Coins']
coll_zh = db['CoinDetails_zh']
coll_hk = db['CoinDetails_hk']

for record in coll_zh.find({}):
    current_des = record.pop('description_zh')
    current_name =  record.pop('chinese_name_zh')
    openCC = OpenCC('s2t')
    new_des = openCC.convert(current_des)
    new_name = openCC.convert(current_name)
    record['description_hk'] = new_des
    record['chinese_name_hk'] = new_name

    count = coll_hk.find({'english_name': record['english_name']}).count()
    if count > 0:
        coll_hk.update({'english_name': record['english_name']}, record)
    else:
        coll_hk.insert(record)

    pass
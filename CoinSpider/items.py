# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CoinspiderItem(scrapy.Item):
    # define the fields for your item here like:
    #_id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    pass

class CoinItem(scrapy.Item):
	code = scrapy.Field()
	english_name = scrapy.Field()
	chinese_name = scrapy.Field()
	exchanger_count = scrapy.Field()
	publish_time = scrapy.Field()
	publish_name = scrapy.Field()
	white_paper = scrapy.Field()
	website = scrapy.Field()
	block_explorer = scrapy.Field()
	is_token = scrapy.Field()
	ico_price = scrapy.Field()
	description = scrapy.Field()
	market_capitalization = scrapy.Field()  # 流通市值
	publish_count = scrapy.Field()  # 发行量
	market_count = scrapy.Field()  # 流通量
	tx_count = scrapy.Field()  # 交易额
	market_ranking = scrapy.Field()
	tx_ranking = scrapy.Field()
	price = scrapy.Field()
	time = scrapy.Field()
	lowest_price = scrapy.Field()
	highest_price = scrapy.Field()
	pass
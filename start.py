# 在scrapy项目中添加start.py文件，用于启动爬虫
from scrapy import cmdline
# 在爬虫运行过程中，会自动将状态信息存储在crawls/storeMyRequest目录下，支持续爬
cmdline.execute('scrapy crawl CoinDetailSpider -s JOBDIR=crawls/storeMyRequest'.split())
# Note:若想支持续爬，在ctrl+c终止爬虫时，只能按一次，爬虫在终止时需要进行善后工作，切勿连续多次按ctrl+c
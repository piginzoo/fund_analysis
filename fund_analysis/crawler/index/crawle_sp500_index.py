import datetime
import pandas_datareader.data as web
from fund_analysis.tools import data_utils

"""
爬取标普500指数值，找了很多，都不靠谱。发现了pandas_datareader，可以直接获得。
"""


start = datetime.datetime(2000, 1, 1)
end = datetime.datetime.today()
SP500 = web.DataReader(name=['sp500'], data_source='fred', start=start, end=end)
print("爬取标普500：%d 行" % len(SP500))
data_utils.save_index_data('SP500',SP500)

# python -m fund_analysis.crawler.index.crawle_sp500_index
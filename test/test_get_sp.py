# ticker='AAPL'
# ticker=wb.DataReader(ticker,start='2019-1-1',data_source='yahoo')
# print("苹果")
# print("="*180)
# print(ticker)

# ticker='sp500'
# ticker=wb.DataReader(ticker,start='1/1/2019',data_source='yahoo')
# print("标普500")
# print("="*180)
# print(ticker)

import datetime

import pandas_datareader.data as web

start = datetime.datetime(2010, 1, 1)
end = datetime.datetime(2020, 1, 27)
SP500 = web.DataReader(['sp500'], 'fred', start, end)
print("标普500")
print("=" * 180)
print(SP500)

# python -m test.test_get_sp

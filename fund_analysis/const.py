from collections import namedtuple

FUND='fund'
STOCK='stock'

NUM_PER_PAGE = 40

DATE_FORMAT = "%Y-%m-%d"

COL_RATE = 'rate'
COL_DATE = '净值日期'
COL_UNIT_NET = '单位净值'
COL_ACCUMULATIVE_NET = '累计净值'
COL_DAILY_RATE = '日增长率'

# Dir and files path
FUND_LIST_FILE = "data/db/fund_list.db"
DB_FILE_BOND_INTEREST = "data/db/bond_interest_CN1YR.db"
DB_FILE = 'data/db/funds.db'
FUND_DATA_DIR = 'data/funds'
INDEX_DATA_DIR = 'data/index' # 指数数据
PLAN_DIR = 'data/plan'
CONF_PATH = 'conf/config.yml'
STOCK_DIR = "data/stocks"

PERIOD_DAY = 'day'  # 天
PERIOD_WEEK = 'week'  # 周
PERIOD_MONTH = 'month'  # 月
PERIOD_QUARTER = 'quarter'  # 季度
PERIOD_YEAR = 'year'  # 季度
PERIOD_ALL = 'all'  # 周+月+季度+年
PERIOD_ALL_ITEMS = [PERIOD_YEAR, PERIOD_QUARTER, PERIOD_MONTH, PERIOD_WEEK]
PERIOD_START_YEAR=1980
PERIOD_NUM={
    PERIOD_DAY:365,
    PERIOD_WEEK: 52,
    PERIOD_MONTH: 12,
    PERIOD_YEAR: 1
}


"""
https://www.joinquant.com/help/api/help#name:index
"""
Index = namedtuple('Index', ['code','name', 'start'])
INDEX = {
    '000001.XSHG': Index('000001.XSHG','上证指数', '1990-12-19'),
    '399001.XSHE': Index('399001.XSHE','深圳成指', '1994-7-20'),
    '399005.XSHE': Index('399005.XSHE','创业板指', '2010-5-31'),
    '000016.XSHG': Index('000016.XSHG','上证50', '2004-1-2'),
    '000300.XSHG': Index('000300.XSHG','沪深300', '2005-4-8'),
    '000905.XSHG': Index('000905.XSHG','中证500', '2004-12-31'),
    'SP500': Index('SP500', '标普500', '2000-1-1')
}


STOCK_INDUSTRY_DEPARTMENT = 'zjw'  # the stock industry class define department

KEYWORD_MIX = '混合型'
KEYWORD_STOCK = '股票型'
KEYWORD_OPEN_FUND = '开放式基金'

DUE_DATE = "2021-01-01"

FUND_MINIMUM_ASSET = 10 * 100000000  # 基金最小资产数，单位亿

PERIOD_NAMES = {
    PERIOD_DAY: '日',
    PERIOD_WEEK: '周',
    PERIOD_MONTH: '月',
    PERIOD_QUARTER: '季',
    PERIOD_YEAR: '年'
}

CRAWLER_INFO = "info"
CRAWLER_TRADE = "trade"
CRAWLER_MANAGER = "manager"

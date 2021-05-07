NUM_PER_PAGE = 40

DATE_FORMAT = "%Y-%m-%d"

COL_DATE = '净值日期'
COL_UNIT_NET = '单位净值'
COL_ACCUMULATIVE_NET = '累计净值'
COL_DAILY_RATE = '日增长率'

FUND_LIST_FILE = "data/db/fund_list.db"
DB_FILE_BOND_INTEREST = "data/db/bond_interest_CN1YR.db"
DB_FILE = 'data/db/funds.db'
FUND_DATA_DIR = 'data/funds'
PLAN_DIR = 'data/plan'
CONF_PATH = 'conf/config.yml'

PERIOD_DAY = 'day'  # 天
PERIOD_WEEK = 'week'  # 周
PERIOD_MONTH = 'month'  # 月
PERIOD_QUARTER = 'quarter'  # 季度
PERIOD_YEAR = 'year'  # 季度
PERIOD_ALL = 'all'  # 周+月+季度+年
PERIOD_ALL_ITEMS = [PERIOD_YEAR, PERIOD_QUARTER, PERIOD_MONTH, PERIOD_WEEK]

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

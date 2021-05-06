import logging

from jqdatasdk import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fund_analysis import const
from fund_analysis.bo.fund import Fund, FundStock, StockIndustry
from fund_analysis.crawler.crawler import Crawler
from fund_analysis.tools import utils

logger = logging.getLogger(__name__)

FUND_TYPES = {
    '401001': '开放式基金',
    '401002': '封闭式基金',
    '401003': 'QDII',
    '401004': 'FOF',
    '401005': 'ETF',
    '401006': 'LOF'
}

FUND_TYPES = {
    '402001': '股票型',
    '402002': '货币型',
    '402003': '债券型',
    '402004': '混合型',
    '402005': '基金型',
    '402006': '贵金属',
    '402007': '封闭式'
}


class JQDataCrawler(Crawler):

    def __init__(self):
        self.login()
        self.session = self.connect_database()

    def login(self):
        conf = utils.load_config()
        uid = str(conf['jqdata']['uid'])
        pwd = conf['jqdata']['pwd']  # 账号是申请时所填写的手机号；密码为聚宽官网登录密码，新申请用户默认为手机号后6位
        logger.info("用户名:%s,密码：%s", uid, pwd)
        auth(uid, pwd)
        logger.info("登录到jqdata成功")

    def crawle_fund(self, code, session):
        fund_info = finance.run_query(query(finance.FUND_MAIN_INFO).filter(finance.FUND_MAIN_INFO.main_code == code))
        if len(fund_info) == 0:
            logger.warning("爬取[%s] '基本信息' 为空，失败", code)
            return None

        portfolio = finance.run_query(query(finance.FUND_PORTFOLIO).filter(
            finance.FUND_PORTFOLIO.code == code).order_by(
            finance.FUND_PORTFOLIO.pub_date.desc()).limit(1))
        if len(portfolio) == 0:
            logger.warning("爬取[%s] '总净值' 为空，失败", code)
            return None

        fund = Fund()
        fund.code = fund_info.loc[0]['main_code']
        fund.name = fund_info.loc[0]['name']
        fund.start_date = fund_info.loc[0]['start_date']
        fund.end_date = fund_info.loc[0]['end_date']
        fund.advisor = fund_info.loc[0]['advisor']
        fund.trustee = fund_info.loc[0]['trustee']
        fund.operate_mode = fund_info.loc[0]['operate_mode']
        fund.fund_type = fund_info.loc[0]['underlying_asset_type']
        fund.total_asset = portfolio.loc[0]['total_asset']
        self.insert_database(session, fund)
        logger.debug("保存了[%s]的基本信息", fund.name)
        return fund

    def connect_database(self):
        # print('sqlite:///' + const.DB_FILE + '?check_same_thread=False')
        engine = create_engine('sqlite:///' + const.DB_FILE + '?check_same_thread=False')  # 是否显示SQL：, echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    def crawle_fund_stocks(self, fund, session):
        stocks = finance.run_query(
            query(finance.FUND_PORTFOLIO_STOCK).filter(finance.FUND_PORTFOLIO_STOCK.code == fund.code).limit(10))
        if len(stocks) == 0:
            logger.warning("爬取[%s:%s] '股票' 为空，失败", fund.code, fund.name)
            return

        for index, row in stocks.iterrows():
            fund_stock = FundStock()
            fund_stock.fund_code = fund.code
            fund_stock.stock_name = row['name']
            fund_stock.stock_code = row['symbol']
            fund_stock.market_cap = row['market_cap']
            fund_stock.proportion = row['proportion']
            self.insert_database(session, fund_stock)

            # if not open_fund, its not Chinese stock, no need to get its industries
            if fund.operate_mode != const.KEYWORD_OPEN_FUND: continue

            stock_industries = self.session.query(StockIndustry).filter(
                StockIndustry.stock_code == fund_stock.stock_code).all()
            if len(stock_industries) > 0:
                logger.debug("股票[%s]行业[%s]已爬取，忽略", fund_stock.stock_name, stock_industries[0].industry_name)
                continue

            industries = get_industry(self.get_market_code(fund_stock.stock_code), date=const.DUE_DATE)
            if len(industries) == 0:
                logger.warning("爬取[%s:%s/%s] '行业信息' 为空，继续", fund.code, fund.name, fund_stock.stock_name)
                continue

            if industries.get(self.get_market_code(fund_stock.stock_code), None) and \
                    industries.get(self.get_market_code(fund_stock.stock_code)).get(const.STOCK_INDUSTRY_DEPARTMENT,
                                                                                    None):
                industry = industries[self.get_market_code(fund_stock.stock_code)][const.STOCK_INDUSTRY_DEPARTMENT]
            else:
                logger.warning("无法找到[%s:%s]的行业分类", self.get_market_code(fund_stock.stock_code), fund_stock.stock_name)
                continue
            industry_code = industry.get('industry_code', None)
            industry_name = industry.get('industry_name', None)
            if industry_name is None or industry_code is None:
                continue

            stock_industry = StockIndustry()
            stock_industry.stock_code = fund_stock.stock_code
            stock_industry.industry_code = industry_code
            stock_industry.industry_name = industry_name
            self.insert_database(session, stock_industry)
            logger.debug("保存了[%s]的[%s]的信息", fund.name, fund_stock.stock_name)

    def crawle_one(self, code):
        """
        crawle one fund information by its code,
        including: basic info, top-10 stocks and their industries
        :param code: fund code
        :return: None(save to db)

        Using JQData API: https://www.joinquant.com/help/api/help#JQData:%E5%85%AC%E5%8B%9F%E5%9F%BA%E9%87%91%E6%95%B0%E6%8D%AE%E5%87%80%E5%80%BC%E7%AD%89
        """

        funds = self.session.query(Fund).filter(Fund.code == code).all()
        if len(funds) == 0:
            fund = self.crawle_fund(code, self.session)
            if fund is None: return False
        else:
            fund = funds[0]
            logger.debug("[%s]基本信息已经爬取过了", fund.name)

        # ignore stock info get if its not a stock fund
        if fund.fund_type != const.KEYWORD_MIX and fund.fund_type != const.KEYWORD_STOCK: return True

        stocks = self.session.query(FundStock).filter(FundStock.fund_code == code).all()
        if len(stocks) == 0:
            self.crawle_fund_stocks(fund, self.session)
        else:
            logger.debug("[%s]的持股信息已爬取[%d]条", fund.name, len(stocks))

        return True

    def insert_database(self, data):
        try:
            self.session.add(data)
            self.session.commit()
        except:
            self.session.rollback()

    def get_market_code(self, code):
        """
        所有沪市股票代码都是60开头的。 深市主板股票是000和001开头的，深市中小板股票是002开头的，深市创业板股票是300开头的
        :return:
        """
        if code.startswith('60'): return code + ".XSHG"
        if code.startswith('000'): return code + ".XSHE"
        if code.startswith('001'): return code + ".XSHE"
        if code.startswith('002'): return code + ".XSHE"
        return code + ".XSHG"

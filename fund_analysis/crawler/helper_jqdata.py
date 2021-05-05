import argparse
import logging

from jqdatasdk import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fund_analysis.bo.fund import Fund, FundStock, StockIndustry
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


def get_fund_info(code):
    conf = utils.load_config()
    uid = str(conf['jqdata']['uid'])
    pwd = conf['jqdata']['pwd']  # 账号是申请时所填写的手机号；密码为聚宽官网登录密码，新申请用户默认为手机号后6位
    logger.info("用户名:%s,密码：%s", uid, pwd)
    auth(uid, pwd)
    logger.info("登录到jqdata成功")
    logger.info("准备获取基金[%s]的信息", code)

    # https://www.joinquant.com/help/api/help#JQData:%E5%85%AC%E5%8B%9F%E5%9F%BA%E9%87%91%E6%95%B0%E6%8D%AE%E5%87%80%E5%80%BC%E7%AD%89
    fund_info = finance.run_query(query(finance.FUND_MAIN_INFO).filter(finance.FUND_MAIN_INFO.main_code == code))

    # portfolio = finance.run_query(query(finance.FUND_PORTFOLIO.code,
    #                                     finance.FUND_PORTFOLIO.code,
    #                                     finance.FUND_PORTFOLIO.period_start,
    #                                     finance.FUND_PORTFOLIO.total_asset).filter(
    portfolio = finance.run_query(query(finance.FUND_PORTFOLIO).filter(
        finance.FUND_PORTFOLIO.code == code).order_by(
        finance.FUND_PORTFOLIO.pub_date.desc()).limit(1))
    logger.debug("---------------------------------------------")
    logger.info("基金[%s]的基本信息：", portfolio)

    stocks = finance.run_query(
        query(finance.FUND_PORTFOLIO_STOCK).filter(finance.FUND_PORTFOLIO_STOCK.code == code).limit(10))
    logger.debug("---------------------------------------------")
    logger.info("基金[%s]的持有股票：", stocks)
    logger.debug("---------------------------------------------")
    for index, row in stocks.iterrows():
        stock_code = row['symbol']
        stock_name = row['name']
        # https://www.joinquant.com/help/api/help#Stock:%E6%9F%A5%E8%AF%A2%E8%82%A1%E7%A5%A8%E6%89%80%E5%B1%9E%E8%A1%8C%E4%B8%9A
        industries = get_industry(stock_code + ".XSHE", date="2021-01-01")
        logger.debug("  ......... ")
        logger.debug("[%s] %s : %r", stock_code, stock_name, industries)

    engine = create_engine('sqlite:///data/db/funds.db?check_same_thread=False', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    # import pdb
    # pdb.set_trace()

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
    session.add(fund)
    logger.debug("保存了[%s]的基本信息", fund.name)

    for index, row in stocks.iterrows():
        fund_stock = FundStock()
        fund_stock.fund_code = fund.code
        fund_stock.stock_name = row['name']
        fund_stock.stock_code = row['symbol']
        fund_stock.market_cap = row['market_cap']
        fund_stock.proportion = row['proportion']
        session.add(fund_stock)
        logger.debug("保存了[%s/%s]的基本信息", fund.name, fund_stock.stock_name)

        industries = get_industry(get_market_code(stock_code), date="2021-01-01")
        if industries.get(get_market_code(stock_code), None) and \
                industries.get(get_market_code(stock_code)).get('zjw', None):
            industry = industries[get_market_code(stock_code)]['zjw']
        else:
            logger.warning("无法找到[%s:%s]的行业分类", get_market_code(stock_code), fund_stock.stock_name)
            continue
        industry_code = industry.get('industry_code', None)
        industry_name = industry.get('industry_name', None)
        if industry_name is None or industry_code is None:
            continue
        stock_industry = StockIndustry()
        stock_industry.stock_code = fund_stock.stock_code
        stock_industry.industry_code = industry_code
        stock_industry.industry_name = industry_name
        session.add(stock_industry)
        logger.debug("保存了[%s/%s]的行业信息", fund.name, fund_stock.stock_name)

    session.commit()


def get_market_code(code):
    """
    所有沪市股票代码都是60开头的。 深市主板股票是000和001开头的，深市中小板股票是002开头的，深市创业板股票是300开头的
    :return:
    """
    if code.startswith('60'): return code + ".XSHG"
    if code.startswith('000'): return code + ".XSHE"
    if code.startswith('001'): return code + ".XSHE"
    if code.startswith('002'): return code + ".XSHE"
    return code + ".XSHG"


# python -m fund_analysis.crawler.helper_jqdata --code 519778
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str)
    args = parser.parse_args()
    utils.init_logger()
    get_fund_info(args.code)

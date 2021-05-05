import argparse
import logging

from jqdatasdk import *

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
    info = finance.run_query(query(finance.FUND_MAIN_INFO).filter(finance.FUND_MAIN_INFO.main_code == code))

    #
    # portfolio = finance.run_query(query(finance.FUND_PORTFOLIO.code,
    #                                     finance.FUND_PORTFOLIO.code,
    #                                     finance.FUND_PORTFOLIO.period_start,
    #                                     finance.FUND_PORTFOLIO.total_asset).filter(
    portfolio = finance.run_query(query(finance.FUND_PORTFOLIO).filter(
        finance.FUND_PORTFOLIO.code == code).order_by(
        finance.FUND_PORTFOLIO.pub_date.desc()).limit(1))
    logger.debug("---------------------------------------------")
    logger.info("基金[%s]的基本信息：", code)
    logger.info("基金[%s]的基本信息：", portfolio)
    logger.debug(info)
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


# python -m test.test_jqdata --code 519778
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str)
    args = parser.parse_args()
    utils.init_logger()
    get_fund_info(args.code)

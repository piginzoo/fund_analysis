import argparse
import logging


from fund_analysis import const
from fund_analysis.crawler.fund.crawler_eastmoney import EastmoneyCrawler
from fund_analysis.crawler.fund.crawler_jqdata_fund import JQDataFundCrawler
from fund_analysis.crawler.stock.crawler_jqdata_stock import JQDataStockCrawler
from fund_analysis.tools import utils

logger = logging.getLogger(__name__)

"""
    爬取所有的内容
"""

# python -m fund_analysis.crawler.crawler --code 519778 --data info
# python -m fund_analysis.crawler.crawler --data info  --num 3
# python -m fund_analysis.crawler.crawler --data trade

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str, default=None)
    parser.add_argument('--type', '-t', type=str, default=None, help="类型：stock/股票,fund/基金")
    parser.add_argument('--sub_type', '-d', type=str, default=None, help="字类型：基金有两种(info：基本信息|trade：交易数据）")
    parser.add_argument('--force', '-f', action='store_true', dest="force", default=False, help="是否再次强制爬取，覆盖已有的")
    parser.add_argument('--num', '-n', type=int, default=999999999, help="爬取条数")
    parser.add_argument('--period', '-p', type=str, default='1d')
    args = parser.parse_args()
    utils.init_logger()

    crawler = None
    if args.type == const.FUND and args.sub_type == const.CRAWLER_INFO:
        crawler = JQDataFundCrawler()
    elif args.type == const.FUND and args.sub_type == const.CRAWLER_TRADE:
        crawler = EastmoneyCrawler()
    elif args.type == const.STOCK:
        crawler = JQDataStockCrawler()
    else:
        logger.error("--data 参数必须是'info|trade'")
        exit()

    if args.code:
        crawler.crawle_one(args.code, args.force, args.period)
    else:
        crawler.crawle_all(args.code, args.num)

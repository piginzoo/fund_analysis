import argparse
import logging

from fund_analysis import const
from fund_analysis.crawler.crawler_eastmoney import EastmoneyCrawler
from fund_analysis.crawler.crawler_jqdata import JQDataCrawler
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
    parser.add_argument('--data', '-d', type=str, default=None)
    parser.add_argument('--force', '-f', action='store_true', dest="force", default=False)
    parser.add_argument('--num', '-n', type=int, default=999999999)
    args = parser.parse_args()
    utils.init_logger()

    crawler = None
    if args.data == const.CRAWLER_INFO:
        crawler = JQDataCrawler()
    elif args.data == const.CRAWLER_TRADE:
        crawler = EastmoneyCrawler()
    else:
        logger.error("--data 参数必须是'info|trade'")
        exit()

    if args.code:
        crawler.crawle_one(args.code,args.force)
    else:
        crawler.crawle_all(args.code, args.num)

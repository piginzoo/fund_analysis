import logging

from jqdatasdk import *

from fund_analysis import const
from fund_analysis.crawler.crawler import Crawler
from fund_analysis.tools import data_utils, jqdata_utils, date_utils
from datetime import datetime

logger = logging.getLogger(__name__)


class JQDataStockCrawler(Crawler):

    def __init__(self):
        jqdata_utils.login()

    def crawle_one(self, code, force=False):
        """
        Using JQData API: https://www.joinquant.com/help/api/help#JQData:%E8%82%A1%E7%A5%A8%E6%A6%82%E5%86%B5
        """
        logger.debug(code)
        code = jqdata_utils.get_market_code(code)
        logger.debug(code)
        stock_info = get_security_info(code)
        if stock_info is None:
            logger.warning("无法获得股票的基本信息：%s",code)
            return

        start_date = stock_info.start_date
        today = datetime.now().date()
        num = date_utils.get_days(from_date=start_date,to_date=today)
        logger.debug("code=%r,num=%d,today=%r",code,num,today)
        df = get_bars(code,
                      num,
                      unit='1d',
                      fields=['date', 'open', 'close', 'high', 'low', 'volume', 'money'],
                      include_now=False,
                      end_dt=today)
        data_utils.save_data(const.STOCK_DIR, "{}.csv".format(code), df, 'date')

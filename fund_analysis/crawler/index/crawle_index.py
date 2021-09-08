# https://zhuanlan.zhihu.com/p/111336040
import logging
import time

from jqdatasdk import get_bars

from fund_analysis.const import INDEX
from fund_analysis.crawler import jqdata_utils
from fund_analysis.tools import date_utils, data_utils, utils
from fund_analysis.tools.date_utils import get_days

logger = logging.getLogger(__name__)


def crawle_index(code, index):
    days = get_days(index.start, date_utils.today())

    # https://www.joinquant.com/help/api/help#JQData:%E6%8C%87%E6%95%B0%E6%A6%82%E5%86%B5
    data = get_bars(security=code,
                    count=days,
                    unit='1d',
                    fields=['date', 'close', 'factor'],
                    end_dt=date_utils.today(),
                    df=True)
    logger.debug("爬取'%s'[%s]数据，从%s至今，一共%d条", index.name, code, index.start, len(data))
    return data


def main():
    jqdata_utils.login()

    for code, index in INDEX.items():
        data = crawle_index(code, index)
        data_utils.save_index_data(code, data, index_label='date')
        time.sleep(1)


# download all index data once
# python -m fund_analysis.crawler.index.crawle_index
if __name__ == '__main__':
    utils.init_logger()
    main()

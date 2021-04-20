import logging
import os
import re

from fund_analysis import utils, conf
from fund_analysis.conf import NUM_PER_PAGE, COL_NAME_DATE
from fund_analysis.utils import get_url, init_logger, get_yesterday, get_days_from_now

logger = logging.getLogger(__name__)


def get_content(code, page, num_per_page=NUM_PER_PAGE, sdate=None, edate=None):
    """
    xxxx,records:2570,pages:65,xxx
    获得整个页数
    """
    if sdate:
        url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={}&page={}&per={}&sdate={}&edate={}'.format(
            code, page, num_per_page, sdate, edate)
    else:
        url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={}&page={}&per={}'.format(
            code, page, num_per_page)
    html = get_url(url)
    return html


def get_page_num(code, sdate=None, edate=None):
    html = get_content(code, 1, NUM_PER_PAGE, sdate, edate)

    # 获取总页数
    pattern = re.compile(r'pages:(.*),')
    result = re.search(pattern, html).group(1)
    page_num = int(result)
    logger.info("代码[%s] 有 %d 页，每页 %d 条", code, page_num, NUM_PER_PAGE)
    return int(page_num)


def get_latest_day(df):
    return df[COL_NAME_DATE].iloc[-1]


def get_missing_days(df, from_date):
    pass


def save_data(code, df):
    dir = conf.DB_DIR
    if not os.path.exists(dir):
        logger.debug("目录[%s]不存在，创建", dir)
        os.makedirs(dir)
    data_path = os.path.join(dir, "{}.csv".format(code))
    df.to_csv(data_path, index=COL_NAME_DATE)
    logger.debug("保存了[%s]", data_path)
    return data_path


def get_start_end_date(code, df):
    if df is None:
        num = get_page_num(code)
        _end = get_yesterday()
        _from = get_days_from_now(num * NUM_PER_PAGE)
        logger.debug("第一次爬取，共[%d]条，从[%s]-->[%s]", num, _from, _end)
        return _from, _end

    latest_day = get_latest_day(df)
    return latest_day, get_yesterday()


# python -m fund_analysis.prepare
if __name__ == '__main__':
    init_logger()
    logger.debug(get_latest_day(utils.load_data(code="161725")))
    logger.debug(get_days_from_now(10))

# 抓取网页
import datetime
import logging
import os

import pandas as pd
import requests

from fund_analysis.conf import COL_NAME_DATE, DB_DIR, DATE_FORMAT

logger = logging.getLogger(__name__)


def get_url(url, proxies=None):
    rsp = requests.get(url, proxies=proxies)
    rsp.raise_for_status()

    logger.debug("成功爬取了：%s", url)
    return rsp.text


def str2date(date_str):
    return datetime.datetime.strptime(date_str, DATE_FORMAT)


def date2str(date):
    return date.strftime(DATE_FORMAT)


def interval_days(from_date, end_date):
    """
    :param from_date: 格式 2021-04-01
    :param end_date:
    :return:
    """
    date_from = datetime.datetime.strptime(from_date, DATE_FORMAT)
    date_end = datetime.datetime.strptime(end_date, DATE_FORMAT)
    interval = date_end - date_from  # 两日期差距
    return interval.days


def get_yesterday():
    return get_days_from_now(1)


def get_days_from_now(num):
    """返回从今天开始往前数num天的日期"""
    today = datetime.datetime.now()
    start_date = today - datetime.timedelta(days=num)
    return start_date.date()  # .date() to reset the time to midnight(00:00)


def init_logger():
    # logging.basicConfig(format='%(asctime)s:%(filename)s:%(lineno)d:%(levelname)s : %(message)s',
    #                     level=logging.DEBUG,
    #                     handlers=[logging.StreamHandler()])
    logging.basicConfig(format='%(levelname)s : %(message)s',
                        level=logging.DEBUG,
                        handlers=[logging.StreamHandler()])


def load_data(code):
    csv_path = os.path.join(DB_DIR, "{}.csv".format(code))

    if not os.path.exists(csv_path):
        logger.error("数据文件 %s 不存在", csv_path)
        return None

    try:
        dateparse = lambda x: datetime.datetime.strptime(x, DATE_FORMAT)
        df = pd.read_csv(csv_path,
                         index_col=COL_NAME_DATE,
                         parse_dates=True,
                         date_parser=dateparse)
    except:
        logger.exception("解析[%s]基金数据失败", code)
        return None
    # logger.info("加载了[%s]数据，行数：%d", csv_path, len(df))
    return df


def save_data(code, df):
    dir = DB_DIR
    if not os.path.exists(dir):
        logger.debug("目录[%s]不存在，创建", dir)
        os.makedirs(dir)
    data_path = os.path.join(dir, "{}.csv".format(code))

    # reindex the date column and sort it
    df = df.sort_index()

    df.to_csv(data_path, index_label=COL_NAME_DATE)
    logger.debug("保存了[%s]", data_path)
    return data_path


def is_date(text):
    try:
        dt = datetime.datetime.strptime(text, DATE_FORMAT)
        return True
    except ValueError:
        return False


# python -m fund_analysis.utils
if __name__ == '__main__':
    assert interval_days('1998-9-1', '2021-04-01') == 8248
    assert interval_days('2021-4-1', '2021-04-10') == 9

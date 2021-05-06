import datetime
import logging
import os

import requests
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fund_analysis import const
from fund_analysis.const import COL_DATE, FUND_DATA_DIR, DATE_FORMAT

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


def is_date(text):
    try:
        dt = datetime.datetime.strptime(text, DATE_FORMAT)
        return True
    except ValueError:
        return False


def load_config():
    if not os.path.exists(const.CONF_PATH):
        raise ValueError("指定的环境配置文件不存在:" + const.CONF_PATH)
    f = open(const.CONF_PATH, 'r', encoding='utf-8')
    result = f.read()
    # 转换成字典读出来
    data = yaml.load(result, Loader=yaml.FullLoader)
    logger.info("读取配置文件:%r", data)
    return data


def connect_database():
    # print('sqlite:///' + const.DB_FILE + '?check_same_thread=False')
    engine = create_engine('sqlite:///' + const.DB_FILE + '?check_same_thread=False')  # 是否显示SQL：, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


# python -m fund_analysis.utils
if __name__ == '__main__':
    assert interval_days('1998-9-1', '2021-04-01') == 8248
    assert interval_days('2021-4-1', '2021-04-10') == 9

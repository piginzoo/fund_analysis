import logging
import os

import requests
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fund_analysis import const

logger = logging.getLogger(__name__)


def get_url(url, proxies=None):
    rsp = requests.get(url, proxies=proxies)
    rsp.raise_for_status()

    logger.debug("成功爬取了：%s", url)
    return rsp.text


def init_logger(level=logging.DEBUG):
    # logging.basicConfig(format='%(asctime)s:%(filename)s:%(lineno)d:%(levelname)s : %(message)s',
    #                     level=logging.DEBUG,
    #                     handlers=[logging.StreamHandler()])
    logging.basicConfig(format='%(levelname)s : %(message)s',
                        level=level,
                        handlers=[logging.StreamHandler()])


def load_config():
    if not os.path.exists(const.CONF_PATH):
        raise ValueError("指定的环境配置文件不存在:" + const.CONF_PATH)
    f = open(const.CONF_PATH, 'r', encoding='utf-8')
    result = f.read()
    # 转换成字典读出来
    data = yaml.load(result, Loader=yaml.FullLoader)
    logger.info("读取配置文件:%r", data)
    return data


def connect_database(echo=False):
    engine = create_engine('sqlite:///' + const.DB_FILE + '?check_same_thread=False',echo=echo)  # 是否显示SQL：, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

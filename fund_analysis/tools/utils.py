import io
import logging
import os
import sys

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



def start_capture_console():
    logger = logging.getLogger()
    original_stdout = sys.stdout  # 保存标准输出流
    original_logger_stdout = logger.handlers[0].stream
    io_stream = io.StringIO("")
    sys.stdout = io_stream
    logger.handlers[0].stream = io_stream
    return io_stream,original_stdout,original_logger_stdout

def end_capture_console(io_stream,original_stdout,original_logger_stdout):
    html = io_stream.getvalue()
    full_html = f'<div class="terminal">\n<pre class="terminal-content">\n{html}\n</pre>\n</div>'
    logger.handlers[0].stream = original_logger_stdout
    sys.stdout = original_stdout
    io_stream.close()
    return full_html
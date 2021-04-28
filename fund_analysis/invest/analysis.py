"""
博迪投资学实践
"""
import os
import random

"""
This is a automatic investment analysis

"""
import argparse
import logging
from fund_analysis import conf
from fund_analysis.conf import COL_DAILY_RATE
from fund_analysis.tools import utils

logger = logging.getLogger(__name__)


def main(args):
    data = utils.load_data(args.code)
    calculate(data)


def calculate(data):
    """

    :param data:
    :return:

    参考：https://blog.csdn.net/robert_chen1988/article/details/80939884
    """

    rate_data = data[COL_DAILY_RATE]
    logger.debug("HEAD:%r", rate_data.head())
    logger.debug(rate_data.describe())
    # logger.debug(rate_date)
    logger.debug(rate_data.skew())


def random_caculate(num):
    files = os.listdir(conf.DB_DIR)
    random.shuffle(files)
    files = files[:num]

    result = None
    for f in files:
        code, _ = os.path.splitext(f)
        data = utils.load_data(code)

        if len(data)<24: continue

        data = data[[COL_DAILY_RATE]]
        if result is None:
            result = data
        else:
            logger.debug("过滤前：%d", len(result))
            intersection_index = data.index.intersection(result.index)
            data = data.loc[intersection_index]
            logger.debug("过滤后：%d", len(result))
            logger.debug("过滤后偏度：%r", data.skew())
            logger.debug("-------------------")
            result = result.add(data)/2
    # logger.debug("最后的结果：%r", result)
    logger.debug("合并后的偏度：%r",result.skew())


# python -m fund_analysis.invest.analysis --code 519778
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str)
    args = parser.parse_args()

    utils.init_logger()
    # main(args)
    random_caculate(100)

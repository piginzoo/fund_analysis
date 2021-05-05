"""
博迪投资学实践
"""
import os
import random

import matplotlib
import matplotlib.pyplot as plt

"""
This is a automatic investment analysis

"""
import argparse
import logging
from fund_analysis import const
from fund_analysis.const import COL_DAILY_RATE
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


def random_caculate(args):
    files = os.listdir(const.DB_DIR)
    random.shuffle(files)

    if args.code:
        num = 1
        files = [args.code+".csv"]
    else:
        num = args.num

    result = None
    counter = 0
    for f in files:
        code, _ = os.path.splitext(f)
        data = utils.load_data(code)

        if data is None: continue
        if len(data) < args.days: continue
        if counter > num: break

        data = data[[COL_DAILY_RATE]]
        if result is None:
            result = data
        else:
            # logger.debug("过滤前：%d", len(result))
            intersection_index = data.index.intersection(result.index)
            data = data.loc[intersection_index]
            result = result.loc[intersection_index]
            # logger.debug("过滤后：%d", len(result))
            logger.debug("偏度：%r", data.skew())
            # logger.debug("-------------------")
            counter += 1
            # logger.debug("Result：%r:%r", result.index[0], result.iloc[0])
            # logger.debug("Data  ：%r:%r", data.index[0], data.iloc[0])
            result = result.add(data)
            # logger.debug("Result：%r:%r", result.index[0], result.iloc[0])
    # logger.debug(result)

    result = result #/ len(result)
    logger.debug(result.describe())
    logger.debug(result.info())
    plot(result[COL_DAILY_RATE])

    logger.debug("从[%d]个基金中筛出[%d]个，跨[%d]天，偏度：%r", len(files), counter, len(result), result.skew())


def plot(data):
    # 设置matplotlib正常显示中文和负号
    matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS']
    matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号
    # 随机生成（10000,）服从正态分布的数据
    """
    绘制直方图
    data:必选参数，绘图数据
    bins:直方图的长条形数目，可选项，默认为10
    normed:是否将得到的直方图向量归一化，可选项，默认为0，代表不归一化，显示频数。normed=1，表示归一化，显示频率。
    facecolor:长条形的颜色
    edgecolor:长条形边框的颜色
    alpha:透明度
    """
    plt.hist(data, bins=100, facecolor="blue", edgecolor="black", alpha=0.7)
    # 显示横轴标签
    plt.xlabel("区间")
    # 显示纵轴标签
    plt.ylabel("频数/频率")
    # 显示图标题
    plt.title("频数/频率分布直方图")
    plt.show()


# python -m fund_analysis.invest.analysis --code 519778
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str, default=None)
    parser.add_argument('--days', '-d', type=int)
    parser.add_argument('--num', '-n', type=int)
    args = parser.parse_args()

    utils.init_logger()
    logging.getLogger('matplotlib.font_manager').disabled = True
    # main(args)
    random_caculate(args)

"""
博迪投资学实践
"""
import os
import random

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

"""
This is a automatic investment analysis

"""
import argparse
import logging
from fund_analysis import const
from fund_analysis.const import COL_DAILY_RATE
from fund_analysis.tools import utils, data_utils, date_utils

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
    files = os.listdir(const.FUND_DATA_DIR)
    random.shuffle(files)

    if args.code:
        num = 1
        files = [args.code + ".csv"]
    else:
        num = args.num

    result = None
    counter = 0

    for f in files:
        code, _ = os.path.splitext(f)
        data = data_utils.load_fund_data(code)

        if data is None: continue

        if data.index[0] > date_utils.str2date(args.start) or \
                data.index[-1] < date_utils.str2date(args.end):
            continue

        # logger.debug("start:%r/%r",data.index[0], date_utils.str2date(args.start))
        # logger.debug("end:%r/%r", data.index[-1], date_utils.str2date(args.end))

        if counter > num: break

        data = data[[const.COL_DAILY_RATE]] # only left rate col
        data.columns = [code] # give him a name

        if result is None:
            result = data
        else:
            result = pd.concat([data, result], axis=1)
            result = result.dropna(how="any",axis=0)

            # logger.debug("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
            # logger.debug("结果2：%r", result)

        counter += 1

    logger.debug("最终结果：\n%r", result)
    logger.debug("=============================================")
    logger.debug("描述    ：\n%r",result.describe())
    logger.debug("=============================================")
    logger.debug('信息    ：\n%r',result.info())
    logger.debug("=============================================")
    logger.debug('协方差  ：\n%r', result.cov())
    logger.debug("=============================================")
    logger.debug('相关系数：\n%r', result.corr())
    # plot(result[const.COL_DAILY_RATE])
    logger.debug("=============================================")
    logger.debug("从[%d]个基金中筛出[%d]个，跨[%d]天，叠加偏度：\n%r", len(files), counter, len(result), result.skew())


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


# python -m fund_analysis.invest.calculate_skewness --code 519778
# python -m fund_analysis.invest.calculate_skewness --start 2019-1-1 --end 2020-12-31 --num 3
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str, default=None)
    parser.add_argument('--start', '-s', type=str)
    parser.add_argument('--end', '-e', type=str)
    parser.add_argument('--num', '-n', type=int)
    args = parser.parse_args()

    utils.init_logger()
    logging.getLogger('matplotlib.font_manager').disabled = True
    # main(args)
    random_caculate(args)

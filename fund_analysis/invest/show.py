import argparse
import logging
import warnings

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pyplot

from fund_analysis.const import COL_DAILY_RATE, COL_ACCUMULATIVE_NET
from fund_analysis.tools import utils, date_utils, data_utils

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", module="matplotlib")

matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 指定默认字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题

logging.getLogger('matplotlib.font_manager').disabled = True
logging.getLogger('matplotlib').disabled = True

logger = logging.getLogger(__name__)


def show_plot(x_data, y_data, x_label, y_label, tilte):
    ax1 = plt.gca()
    ax1.plot(x_data, y_data)
    ax1.set_ylabel(y_label)
    # ax1.set_xlabel(x_label)
    ax1.legend(loc='upper left')
    plt.title(tilte)


def show_hist(data):
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
    data = data[COL_DAILY_RATE]
    plt.hist(data, bins=100, facecolor="blue", edgecolor="black", alpha=0.7)
    # # 显示横轴标签
    # plt.xlabel("区间")
    # 显示纵轴标签
    plt.ylabel("天数")
    # 显示图标题
    plt.title("日增长率直方图")


def main(args):
    data = data_utils.load_fund_data(args.code)
    # 获取净值日期、单位净值、累计净值、日增长率等数据
    date = data.index
    accumulative_net_value = data[COL_ACCUMULATIVE_NET]
    daily_growth_rate = data[COL_DAILY_RATE]

    plt.subplot(311)
    show_plot(x_data=date, y_data=accumulative_net_value, x_label='日期', y_label='累计净值', tilte='累计净值')
    plt.subplot(312)
    show_plot(x_data=date, y_data=daily_growth_rate, x_label='日期', y_label='日增长率', tilte='日增长率')
    plt.subplot(313)
    show_hist(data)

    logger.info('日增长率 缺失      ：%r', sum(np.isnan(daily_growth_rate)))
    logger.info('日增长率 正天数     ：%r', sum(daily_growth_rate > 0))
    logger.info('日增长率 负天数(<=0)：%r', sum(daily_growth_rate <= 0))
    logger.info("日收益率 均值      ：%r", data.mean().values)
    logger.info("日收益率 方差      ：%r", data.var().values)
    logger.info("日收益率 偏度      ：%r", data.skew().values)

    # set window title
    fig = pyplot.gcf()
    fig.canvas.set_window_title('基金：' + args.code + ' 数据')

    # maximize the window
    # 如果显示报错，注释掉这两行，这个是默认TkAgg的处理：https://stackoverflow.com/questions/12439588/how-to-maximize-a-plt-show-window-using-python/23755272
    manager = plt.get_current_fig_manager()
    manager.window.state('zoomed')

    plt.show()


# python -m fund_analysis.invest.show --code 519778
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str, default=None)
    args = parser.parse_args()

    utils.init_logger()
    main(args)

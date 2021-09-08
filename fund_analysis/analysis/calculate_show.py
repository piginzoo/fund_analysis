import argparse
import logging
import math
import warnings

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pyplot

from fund_analysis.analysis.base_calculator import BaseCalculator
from fund_analysis.bo.fund import Fund, FundStock
from fund_analysis.bo.fund_industry import FundIndustry
from fund_analysis.const import COL_DAILY_RATE, COL_ACCUMULATIVE_NET
from fund_analysis.tools import utils, data_utils
from fund_analysis.tools.date_utils import get_days, date2str

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", module="matplotlib")

matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 指定默认字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题

logging.getLogger('matplotlib.font_manager').disabled = True
logging.getLogger('matplotlib').disabled = True

logger = logging.getLogger(__name__)


class ShowCalculater(BaseCalculator):

    def name(self):
        return "Show:展示股票/基金的基本信息"

    def plot(self, data):
        data, index_close_price, max_withdraw, start, year, aagr, total_profit = data
        date = data.index
        accumulative_net_value = data[COL_ACCUMULATIVE_NET]
        daily_growth_rate = data[COL_DAILY_RATE]

        plt.subplot(311)

        # 合并一下基金和指数数据
        fund_index_data = data_utils.merge_by_date([accumulative_net_value, index_close_price])

        # 归一化一下，防止太大，显示不下，Y方向上
        fund_index_data[[COL_ACCUMULATIVE_NET]] = fund_index_data[[COL_ACCUMULATIVE_NET]] / \
                                                  fund_index_data[[COL_ACCUMULATIVE_NET]].max()
        fund_index_data[['rate']] = fund_index_data[['rate']] / fund_index_data[['rate']].max()

        self.show_plot(x_data=fund_index_data.index,
                       y_data=fund_index_data,
                       x_label='日期',
                       y_label='累计净值',
                       tilte='累计净值',
                       labels=['基金', '指数'])

        plt.subplot(312)
        self.show_plot(x_data=date,
                       y_data=daily_growth_rate,
                       x_label='日期',
                       y_label='日增长率',
                       tilte='日增长率')
        plt.subplot(313)
        self.show_hist(data)

        # set window title
        fig = pyplot.gcf()
        fig.canvas.set_window_title('基金/股票数据')

        # maximize the window
        # 如果显示报错，注释掉这两行，这个是默认TkAgg的处理：https://stackoverflow.com/questions/12439588/how-to-maximize-a-plt-show-window-using-python/23755272
        # manager = plt.get_current_fig_manager()
        # manager.window.state('zoomed')
        # plt.show()
        return plt

    def show_plot(self, x_data, y_data, x_label, y_label, tilte, labels=[]):
        ax1 = plt.gca()
        ax1.plot(x_data, y_data)
        ax1.set_ylabel(y_label)
        ax1.set_xlabel(x_label)
        ax1.legend(loc='upper left')
        plt.legend(labels=labels, loc='best')
        plt.title(tilte)

    def show_hist(self, data):
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

    def load_data(self, args):
        data = data_utils.load_fund_data(args.code)
        if data is None:
            raise ValueError("数据不存在，代码：" + args.code)

        index_data = data_utils.load_index_data_by_name('上证指数')
        index_rate = data_utils.calculate_rate(index_data, 'close')

        self.load_info(args.code)

        return data, index_data, index_rate

    def load_info(self, code):
        session = utils.connect_database()

        def format(bo):
            if type(bo) == list:
                # contens = "\n".join([format(__bo) for __bo in bo])
                # return contens
                for __bo in bo:
                    format(__bo)
            else:
                info = bo.get_info()
                # contents = [str(k) + ":\t" + str(v) for k, v in info.items()]
                # contents = "\n".join(contents)
                # return contents
                for k, v in info.items():
                    logger.info("%r : %r", k, v)

        fund = session.query(Fund).filter(Fund.code == code).limit(1).first()
        fund_industries = session.query(FundStock).filter(FundStock.fund_code == code).all()
        fund_stocks = session.query(FundIndustry).filter(FundIndustry.code == code).all()
        logger.info("------------------------------")
        format(fund)
        logger.info("------------------------------")
        format(fund_industries)
        logger.info("------------------------------")
        format(fund_stocks)

        # 获取净值日期、单位净值、累计净值、日增长率等数据
        # date = data.index
        # accumulative_net_value = data[COL_ACCUMULATIVE_NET]
        # daily_growth_rate = data[COL_DAILY_RATE]

    def calculate(self, _data):
        data, index_close_price, index_rate = _data

        daily_growth_rate = data[COL_DAILY_RATE]

        max_withdraw = self.calculate_withdraw(data[[COL_ACCUMULATIVE_NET]])
        start, year, total_profit, aagr = self.calculate_AAGR(data[[COL_ACCUMULATIVE_NET]])

        logger.info('日增长率 缺失      ：%r', sum(np.isnan(daily_growth_rate)))
        logger.info('日增长率 正天数     ：%r', sum(daily_growth_rate > 0))
        logger.info('日增长率 负天数(<=0)：%r', sum(daily_growth_rate <= 0))
        logger.info("日收益率 均值      ：%.2f%%", data[[COL_DAILY_RATE]].mean().values[0])
        logger.info("日收益率 方差      ：%.2f%%", data[[COL_DAILY_RATE]].var().values[0])
        logger.info("日收益率 偏度      ：%.2f%%", data[[COL_DAILY_RATE]].skew().values[0])
        logger.info("最大回撤率         ：%.2f%%", max_withdraw * 100)
        logger.info("年平均投资回报率   ：%.2f%%", aagr * 100)
        logger.info("总收益率          ：%.2f%%", total_profit * 100)

        return data, index_close_price, max_withdraw, start, year, aagr, total_profit

    def calculate_withdraw(self, data):
        """
        最大回撤：先找到最低的价格，然后往前回溯，最高的价格，然后计算回撤率
        参考：http://fund.eastmoney.com/a/202011191706731233.html
        """
        min_index = data.idxmin().values[0]
        max_index = data[:min_index].idxmax().values[0]
        # import pdb; pdb.set_trace()
        withdraw_rate = (data.loc[max_index] - data.loc[min_index]) / data.loc[max_index]
        return withdraw_rate.values[0]

    def calculate_AAGR(self, data):
        """
        计算平均年化收益率
        # 参考： https://zhuanlan.zhihu.com/p/63121208
        (期末/期初)^(1/周期) - 1，周期可以是分数，比如是3.2，具体就不推导了
        2020.5.1 ~ 2021.3.6 , 计算出delta，
        # 对银行存款、票据、债券等D=360日，对于股票、期货等市场D=250日，对于房地产和实业等D=365日。
        """
        p0 = data.iloc[0].values[0]
        p1 = data.iloc[-1].values[0]
        p0_date = data.index[0]
        p1_date = data.index[-1]

        total_profit = (p1 - p0) / p0
        days = get_days(p0_date, p1_date)
        year = days / 250
        rate_per_year = math.pow(p1 / p0, 1 / year) - 1
        logger.debug("[%s] %.2f  --(%.1f年)--> [%s] %.2f  : 年化收益率 %.2f ",
                     date2str(p0_date), p0, year, date2str(p1_date), p1, rate_per_year)

        return date2str(p0_date), year, total_profit, rate_per_year

    def get_arg_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--code', '-c', type=str, default=None)
        return parser


# python -m fund_analysis.analysis.calculate_show --code 519778
if __name__ == '__main__':
    utils.init_logger()
    calculator = ShowCalculater()
    calculator.main(args=None, console=True)

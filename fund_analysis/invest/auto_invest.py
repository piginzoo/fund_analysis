"""
This is a automatic investment analysis

"""
import argparse
import logging
import time

from fund_analysis import const
from fund_analysis.const import COL_ACCUMULATIVE_NET, PERIOD_NAMES
from fund_analysis.tools import utils, data_utils

logger = logging.getLogger(__name__)


def main(args):
    data = data_utils.load_fund_data(args.code)

    if data is None: return

    data = data.loc[args.start:args.end]
    start_time = time.time()

    invest_data = filter_invest_by(data, args.period, args.day)
    # print(invest_data.info())
    # print(invest_data.describe())
    # print(invest_data)

    price_of_last_day = data[[COL_ACCUMULATIVE_NET]].iloc[-1]

    # print(invest_data.info())
    logger.debug("最后一天[%s]的价格为：%.2f", invest_data.index[-1], price_of_last_day)
    profit_percentage = invest(invest_data, price_of_last_day)
    logger.info("代码[%s] 按[%s]定投 %d 次, [%s] -> [%s] 定投收益率: %.3f%%, 耗时: %.2f",
                args.code,
                PERIOD_NAMES[args.period],
                len(invest_data),
                args.start,
                args.end,
                profit_percentage * 100 - 100,
                time.time() - start_time)


def invest(invest_data, price_of_last_day):
    '''
    the profit = \frac{(\sum_{i=1}^{N} \frac{1}{p_i} )\times p_{N}}{N}
    '''
    sum_1_devide_price = 0
    for i in range(len(invest_data)):
        price_net = invest_data[[COL_ACCUMULATIVE_NET]].iloc[i]
        sum_1_devide_price += 1 / price_net
    profit_percentage = (sum_1_devide_price * price_of_last_day) / len(invest_data)

    return profit_percentage


def filter_invest_by(data, period, day):
    """
    根据过滤日期的类型<period:week,day,month>，和 day（第几天）来过滤数据
    思路是遍历每一天的数据，如果这一天可以和day对上，就确定这条数据，

    但是这里有个bug，就是那天可能是休息日，比如每月1号定投，但是10.1号是公共假日，就没有交易数据，
    这种情况下，就需要向后顺延，直到可以找到有交易数据，但是对周而言，可能会一周都是休息日，那么就要忽略这周了。

    :param data: 按照index日期排序过的
    :param period: 日期类型
    :param day: 第几日，比如周3，或者每月第3日
    :return:
    """
    indices = []

    current_month = None
    is_invested_this_month = False
    for date, one in data.iterrows():

        if current_month != date.month:
            # if current_month: logger.debug("从[%d]月=>[%d]月", current_month, date.month)
            is_invested_this_month = False
            current_month = date.month

        # invest everyday
        if period == const.PERIOD_DAY:
            indices.append(date)

        # only invest at Monday, but wierd is, date.weekday() is from 0 ~ 6
        if period == const.PERIOD_WEEK and date.weekday() + 1 == day:
            indices.append(date)

        # only invest by day of each month
        if period == const.PERIOD_MONTH and date.day >= day:
            if date.day == day:
                indices.append(date)
                is_invested_this_month = True
                continue
            if not is_invested_this_month:
                logger.debug("这个[%d]月，不是第[%d]号投(假日)，而是顺延到[%d]号投的", date.month, day, date.day)
                indices.append(date)
                is_invested_this_month = True
                continue

    logger.debug("数据经过[%s]过滤,剩余%d条", period, len(indices))
    return data.loc[indices]


# python -m fund_analysis.auto_invest --code 519778 --start 2020-01-01 --end 2021-04-22 --period month --day 12
# python -m fund_analysis.auto_invest --code 001938 --start 2020-01-07 --end 2021-04-22 --period month --day 13 # 30.61%
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str)
    parser.add_argument('--start', '-s', type=str)
    parser.add_argument('--end', '-e', type=str)
    parser.add_argument('--period', '-p', type=str)  # week,day,month
    parser.add_argument('--day', '-d', type=int, default=1)  # 每周、每月几号
    args = parser.parse_args()

    utils.init_logger()
    main(args)

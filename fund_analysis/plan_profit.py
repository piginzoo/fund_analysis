"""
This is a automatic investment analysis

"""
import argparse
import logging
import time
from datetime import datetime

from fund_analysis import utils, conf
from fund_analysis.conf import COL_ACCUMULATIVE_NET, PERIOD_NAMES

logger = logging.getLogger(__name__)


def main(args):
    data = utils.load_data(args.code)

    if data is None: return

    data = data.loc[args.start:args.end]
    start_time = time.time()

    invest_data = filter_invest_by(data, args.period, args.day)
    # print(data.info())
    # print(data.describe())
    # print(invest_data)

    price_of_last_day = invest_data[[COL_ACCUMULATIVE_NET]].iloc[-1]

    # print(invest_data.info())
    logger.debug("最后一天[%s]的价格为：%.2f", invest_data.index[-1], price_of_last_day)
    profit_percentage = invest(invest_data, price_of_last_day)
    logger.info("代码[%s] 按[%s]定投 %d 次, [%s] -> [%s] 定投收益率: %.3f%%, 耗时: %.2f",
                args.code,
                PERIOD_NAMES[args.period],
                len(invest_data),
                args.start,
                args.end,
                profit_percentage * 100,
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
    indices = []

    for date_index, one in data.iterrows():
        date = datetime.strptime(date_index, "%Y-%m-%d")

        # invest everyday
        if period == conf.PERIOD_DAY:
            # candidate_df.append(one)
            indices.append(date_index)

        # only invest at Monday
        if period == conf.PERIOD_WEEK and date.weekday() == day:
            # candidate_df.append(one)
            indices.append(date_index)

        # only invest at first day of each month

        if period == conf.PERIOD_MONTH and date.day == day:
            # candidate_df.append(one)
            indices.append(date_index)

    logger.debug("数据经过[%s]过滤,剩余%d条", period, len(indices))
    return data.loc[indices]


# python -m fund_analysis.auto_invest --code 519778 --start 2020-01-01 --end 2021-04-22 --period week --day 12
# python -m fund_analysis.auto_invest --code 001938 --start 2020-01-07 --end 2021-04-22 --period week --day 13 # 30.61%
# python -m fund_analysis.auto_invest --code 001938 --start 2020-01-07 --end 2021-04-22 --period week --day 13 # 30.61%
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

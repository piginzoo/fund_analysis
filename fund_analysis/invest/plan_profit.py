"""
This is a automatic investment analysis

"""
import argparse
import logging
import time
from datetime import datetime

from fund_analysis import conf
from fund_analysis.conf import COL_ACCUMULATIVE_NET, PERIOD_NAMES
from fund_analysis.invest import plan_loader
from fund_analysis.tools import utils

logger = logging.getLogger(__name__)


def main(args):
    invest_records = plan_loader.load(args.plan)

def filter_invest_by(data, invest_records):
    """
    invest_records actually is virtual invest day, or you can call it fake day,
    because it did not consider the holidays, or weekend,
    so, we need to compare with the real fund data,
    the logic is quiet simple:
    Iterate the invest_records,get current invest_record, compare it with the fund date,
    if not match, just move current fund date to next day,
    then continue to see whether it is same as current invest day, if not, continue next fund day,
    ...
    util, the fund day reach to next invest_record day, means, no proper day to invest, give up.
    if any day matched during the loop, just find the proper invest day.
    """
    indices = []

    current_month = None
    is_invested_this_month = False
    for date_index, one in data.iterrows():

        date = datetime.strptime(date_index, "%Y-%m-%d")
        if current_month!= date.month:
            # if current_month: logger.debug("从[%d]月=>[%d]月", current_month, date.month)
            is_invested_this_month = False
            current_month = date.month

        # invest everyday
        if period == conf.PERIOD_DAY:
            indices.append(date_index)

        # only invest at Monday, but wierd is, date.weekday() is from 0 ~ 6
        if period == conf.PERIOD_WEEK and date.weekday()+1 == day:
            indices.append(date_index)

        # only invest at first day of each month
        if period == conf.PERIOD_MONTH and date.day >= day:
            if date.day == day:
                indices.append(date_index)
                is_invested_this_month = True
                continue
            if not is_invested_this_month:
                logger.debug("这个[%d]月，不是第[%d]号投(假日)，而是顺延到[%d]号投的",date.month,day,date.day)
                indices.append(date_index)
                is_invested_this_month = True
                continue

    logger.debug("数据经过[%s]过滤,剩余%d条", period, len(indices))
    return data.loc[indices]


# 30.61%
# python -m fund_analysis.plan_profit --code 519778 --start 2020-01-01 --end 2021-04-22 --period week --day 12
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str)
    parser.add_argument('--plan', '-p', type=str)
    args = parser.parse_args()

    utils.init_logger()
    main(args)

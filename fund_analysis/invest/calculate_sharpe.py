import argparse
import logging
from datetime import datetime

from pandas import DataFrame

from fund_analysis import const
from fund_analysis.bo.fund import Fund
from fund_analysis.const import DATE_FORMAT
from fund_analysis.tools import utils, data_utils, date_utils

logger = logging.getLogger(__name__)

"""
Reference:
 <https://zh.wikipedia.org/wiki/%E5%A4%8F%E6%99%AE%E6%AF%94%E7%8E%87>
 <math>S_a = \frac{E[R_a-R_b]}{\sigma_a} = \frac{E[R_a-R_b]}{\sqrt{\mathrm{var}[R_a-R_b]}},</math>
 
 let's calculate everyone's Sharpe Ratio:
 - it must be '混合型' or '股票型'
 - its start date must be from 2018.1.1 ( 3 years+)
 - we use '1年期国债利率' as basic profit
 - the sampling interval is a quarter( 3 months)
"""


def filter_interest_by_period(bond_interests, periods):
    result = []
    for period in periods:
        start = period[0]
        end = period[1]
        data = bond_interests.loc[start:end]
        if len(data) == 0:
            logger.debug("无法过滤出基准利率[%r:%r]", date_utils.date2str(start), date_utils.date2str(end))
            result.append(None)
        elif len(data) == 1:
            result.append(data.iloc[0])
        else:
            logger.debug("过滤出多条基准利率[%r:%r]：%d", start, end, len(data))
            result.append(data.iloc[0])

    return result


def filter_trade_by_period(data, periods):
    result = []
    for period in periods:
        start = period[0]
        end = period[1]
        filter_data = data.loc[start:end]

        if len(filter_data) == 0:
            # logger.debug("无法过滤出[%r~%r]的净值数据，忽略", date_utils.date2str(start), date_utils.date2str(end))
            continue

        if len(filter_data) < 3:
            logger.debug("过滤出[%r~%r]的净值数据小于2条，舍弃", date_utils.date2str(start), date_utils.date2str(end))
            continue

        rate = (filter_data.iloc[-1][const.COL_ACCUMULATIVE_NET] - \
                filter_data.iloc[0][const.COL_ACCUMULATIVE_NET]) / \
               filter_data.iloc[0][const.COL_ACCUMULATIVE_NET]

        result.append([filter_data.index[-1], rate])

    df = DataFrame(result, columns=['date', 'rate'])
    df.set_index(['date'], inplace=True)
    return df


def calculate_one_fund(fund, asset, period, session):
    # if fund.type != const.KEYWORD_MIX and fund.type != const.KEYWORD_STOCK:
    #     logger.warning("基金不是混合&股票型：类型=%s", fund.type)
    #     return None

    funds = session.query(Fund).filter(Fund.code == fund.code).all()
    if len(funds) != 1:
        logger.warning("基金 [%s] 在基金表[funds] 中不存在", fund.name)
        return None
    fund = funds[0]

    if fund.total_asset < asset:
        logger.warning("基金总资产[%f]小于[%f]，忽略", fund.total_asset, asset)
        return None

    start_year = date_utils.date2str(fund.start_date)
    end_year = date_utils.date2str(datetime.now().date())
    logger.info("[%s:%s] %r~%r 夏普指数：", fund.code, fund.name, start_year, end_year)

    if period == const.PERIOD_ALL:
        return [calculate_one_fund_by_period(fund, p) for p in const.PERIOD_ALL_ITEMS]
    else:
        return calculate_one_fund_by_period(fund, period)


def calculate_one_fund_by_period(fund, period):
    # # 不计算今年才开始的基金
    # if fund.start_date > datetime.strptime('2020-1-1', DATE_FORMAT).date():
    #     logger.debug("此基金开始日期[%r]，太新了，不具备分析价值")
    #     return None

    start_year = fund.start_date.year
    end_year = datetime.now().date().year

    periods = []
    for year in range(start_year, end_year + 1):
        periods += date_utils.get_peroid(year, period)

    trade_data = data_utils.load_fund_data(fund.code)
    if trade_data is None:
        return None

    data = filter_trade_by_period(trade_data, periods)
    logger.debug("过滤出%d条基金净值记录，%r~%r", len(data), data.index[0], data.index[-1])

    bond_interests = data_utils.load_bond_interest_data(data.index)
    logger.debug("过滤出%d条基准利率记录", len(bond_interests))

    # assert len(data) == len(bond_interests), "基金净值数据 ~ 基准利率 个数不一致"
    sharpe_ratio = calculate_sharpe(data, bond_interests, period)

    return sharpe_ratio


def calculate_sharpe(fund_rates, bond_interests, period):
    """
    :param fund_data:
    :param bond_interest:
    :param period:
    :return:
    """
    factor = 1
    if period == const.PERIOD_YEAR:
        factor = 1
    if period == const.PERIOD_QUARTER:
        factor = 4
    if period == const.PERIOD_MONTH:
        factor = 12
    if period == const.PERIOD_WEEK:
        factor = 52

    logger.info("--------")
    logger.info("基金[%s]收益均值  ：%.2f%%", const.PERIOD_NAMES[period], fund_rates.mean() * 100)
    logger.info("基金[%s]收益标准差：%.2f%%", const.PERIOD_NAMES[period], fund_rates.std() * 100)
    logger.info("国债[%s]基准利率  ：%.2f%%", const.PERIOD_NAMES[period], bond_interests.mean() / factor)
    sharpe_ratio = (fund_rates.mean() * 100 - bond_interests.mean() / factor) / (fund_rates.std() * 100)
    logger.info("按[%s]计算夏普指数：%.2f", const.PERIOD_NAMES[period], sharpe_ratio)

    return sharpe_ratio


def main(code, asset, period):
    session = utils.connect_database()

    fund_list = data_utils.load_fund_list()

    if code:
        fund = data_utils.load_fund(code)
        calculate_one_fund(fund, asset, period, session)
    else:
        for fund in fund_list:
            calculate_one_fund(fund, asset, period, session)
            logger.info("=============================================")


# python -m fund_analysis.invest.calculate_sharpe --code 519778 --asset 10 --period month
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str, default=None)
    parser.add_argument('--asset', '-a', type=int, default=10)  # 至少多少亿的盘子
    parser.add_argument('--period', '-p', type=str)  # year|month|quarter
    args = parser.parse_args()
    code = args.code
    asset = args.asset * 100000000  # 亿
    period = args.period

    utils.init_logger(logging.DEBUG)
    main(args.code, args.asset, args.period)

"""
This is a automatic investment analysis

"""
import argparse
import logging

from fund_analysis.const import COL_ACCUMULATIVE_NET, COL_DATE
from fund_analysis.invest import plan_loader
from fund_analysis.tools import utils

logger = logging.getLogger(__name__)


class RealInvestRecord():
    def __init__(self, fund_data, invest_record):
        self.fund_data = fund_data
        self.invest_record = invest_record


def profit(real_invest_data, last_day_price, charge_buy_rate,charge_sell_rate):
    """
    calculate the profit by the filtered data.
    :param real_invest_data:
    :param last_day_price:
    :param charge_buy_rate:
    :param charge_sell_rate:
    :return:
    """
    total_share = 0.0
    total_investment = 0.0
    total_pure_investment = 0.0
    total_redeem = 0.0
    total_charge = 0.0

    logger.debug("-----------------------------------")
    for data in real_invest_data:
        price = data.fund_data[COL_ACCUMULATIVE_NET]
        date = utils.date2str(data.invest_record.date)

        amount = data.invest_record.amount

        if amount>0:
            total_investment += amount
            charge_amount = amount * charge_buy_rate
            total_pure_investment += (amount - charge_amount)
        else:
            charge_amount = abs(amount * charge_sell_rate) # notice: use abs
            total_redeem += abs(amount - charge_amount)

        total_charge += charge_amount
        exclude_charge_amount = amount - charge_amount
        share = exclude_charge_amount / price  # the bought share in the trade day
        total_share += share

        logger.debug("[%r] 按价格[%.3f],花费[%.3f]元,扣除手续费[%.3f]后，购买[%.3f]份额",
                     date, price, amount, abs(charge_amount), share)


    total_assets = last_day_price * total_share

    # calcluate the profit need to deduct the charge
    profit = (total_assets +  total_redeem + total_charge) / total_pure_investment - 1
    pure_profit = (total_assets + total_redeem ) / total_investment - 1

    return profit, pure_profit, total_assets, total_investment, total_share, total_charge, total_redeem


def get_real_invest_data(fund_data, invest_records):
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
    fund_date_pointer = 0
    invest_date_pointer = 0

    real_invest_records = []
    while True:
        fund_date = fund_data.index[fund_date_pointer]

        invest_date = invest_records[invest_date_pointer].date
        if invest_date <= fund_date:
            logger.debug("确认[%s]投资[%.2f]", fund_date, invest_records[invest_date_pointer].amount)
            real_invest_records.append(
                RealInvestRecord(fund_data.iloc[fund_date_pointer],
                                 invest_records[invest_date_pointer])
            )
            invest_date_pointer += 1
            fund_date_pointer += 1

        if invest_date > fund_date:
            fund_date_pointer += 1
            # logger.debug("投资日[%s]>基金日[%s]，基金日后移", invest_date, fund_date)

        if invest_date_pointer >= len(invest_records):
            logger.debug("投资日结束")
            break
        if fund_date_pointer >= len(fund_data):
            logger.debug("基金日结束")
            break
    return real_invest_records


def main(args):
    # get the invest day&amount, but notice, teh day maybe is not a 'real' invest day for holiday or other reasons
    logger.debug("加载投资计划：%s", args.plan)
    logger.debug("-----------------------------------")
    invest_records = plan_loader.load(args.plan)
    logger.debug("-----------------------------------")
    if not invest_records: return

    fund_data = utils.load_data(args.code)
    price_of_last_day = fund_data[[COL_ACCUMULATIVE_NET]].iloc[-1]

    real_invest_data = get_real_invest_data(fund_data, invest_records)

    profit_percentage, pure_profit, total_assets, total_investment, total_share, total_charge, total_redeem = \
        profit(real_invest_data, price_of_last_day, args.charge_buy, args.charge_sell)

    logger.info(
        "\n基金代码:\t %s ,\
        \n基金利润:\t%.3f%%,\
        \n实际利润:\t%.3f%%,\
        \n投资金额:\t%.3f 元,\
        \n手续费  :\t%.3f 元,\
        \n实投金额:\t%.3f 元,\
        \n总份额  :\t%.3f 份, \
        \n资产价值:\t%.3f 元,\
        \n获利金额:\t%.3f 元，\
        \n投资次数:\t%d 次",
        args.code,
        profit_percentage * 100,
        pure_profit * 100,
        total_investment,
        total_charge,
        total_investment - total_charge,
        total_share,
        total_assets,
        total_assets - total_investment + total_charge + total_redeem,
        len(real_invest_data))


# 30.61%
# python -m fund_analysis.invest.plan_profit --code 001938 --plan=data/plan/jq_001938.tx
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str)
    parser.add_argument('--plan', '-p', type=str)
    parser.add_argument('--charge_buy', '-b', type=float, default=0.015)
    parser.add_argument('--charge_sell', '-s', type=float, default=0.005)
    args = parser.parse_args()

    utils.init_logger()
    main(args)

"""
This is a automatic investment analysis

"""
import argparse
import logging

from fund_analysis.conf import COL_ACCUMULATIVE_NET
from fund_analysis.invest import plan_loader
from fund_analysis.tools import utils

logger = logging.getLogger(__name__)


class RealInvestRecord():
    def __init__(self, fund_data, invest_record):
        self.fund_data = fund_data
        self.invest_record = invest_record


def profit(real_invest_data, last_day_price):
    total_share = 0.0
    total_investment = 0.0
    for data in real_invest_data:
        price = data.fund_data[COL_ACCUMULATIVE_NET]
        amount = data.invest_record.amount
        share = amount / price  # 当日购买的份额
        # print(total_share,",",share)
        total_share += share
        total_investment += amount
    total_assets = last_day_price * total_share
    profit = (total_assets - total_investment) / total_investment
    return profit, total_assets, total_investment


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
            logger.debug("确认[%s]投资[%.2f]", fund_date,invest_records[invest_date_pointer].amount )
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
    logger.debug("加载投资计划：%s",args.plan)
    logger.debug("-----------------------------------")
    invest_records = plan_loader.load(args.plan)
    logger.debug("-----------------------------------")
    if not invest_records: return

    fund_data = utils.load_data(args.code)
    price_of_last_day = fund_data[[COL_ACCUMULATIVE_NET]].iloc[-1]
    real_invest_data = get_real_invest_data(fund_data, invest_records)
    profit_percentage, total_assets, total_investment = profit(real_invest_data, price_of_last_day)
    logger.info("\n基金代码:\t %s ,\n投资计划获利:\t%.4f%% ，\n总投资金额:\t%.2f , \n总账面资产价值:\t%.2f ，\n合计获利金额:\t%.2f ，\n合计投资天数:\t%d 天",
                args.code,
                profit_percentage*100,
                total_investment,
                total_assets,
                total_assets - total_investment,
                len(real_invest_data))


# 30.61%
# python -m fund_analysis.invest.plan_profit --code 001938 --plan=data/plan/jq_001938.txt
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str)
    parser.add_argument('--plan', '-p', type=str)
    args = parser.parse_args()

    utils.init_logger()
    main(args)

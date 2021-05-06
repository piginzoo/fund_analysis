import argparse
from datetime import datetime

from fund_analysis import const
from fund_analysis.bo.fund import Fund
from fund_analysis.const import DATE_FORMAT
from fund_analysis.invest import auto_invest
from fund_analysis.tools import utils, data_utils

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


def main(code,asset,period):
    session = utils.connect_database()

    fund_list = utils.load_fund_list()

    for fund in fund_list:

        if fund.type != const.KEYWORD_MIX and fund.type != const.KEYWORD_STOCK: continue

        funds = session.query(Fund).filter(Fund.code == fund.code).all()
        if len(funds) != 1: continue
        fund = funds[0]

        if fund<asset: continue

        if fund.start_date> datetime.strptime('2020-1-1',DATE_FORMAT): continue

        trade_data = data_utils.load_fund_data(fund.code)

        data_utils.load_bond_interest_data()

        auto_invest.filter_invest_by(trade_data,)

# python -m fund_analysis.invest.show --code 519778
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str, default=None)
    parser.add_argument('--asset', '-a', type=int, default=10) # 至少多少亿的盘子
    parser.add_argument('--period', '-p', type=str)  # year|month|quarter
    args = parser.parse_args()
    code = args.code
    asset = args.asset * 100000000 # 亿

    utils.init_logger()
    main(args)

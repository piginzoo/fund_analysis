from fund_analysis import const
from fund_analysis.bo.fund import Fund
from fund_analysis.tools import utils

session = utils.connect_database()

fund_list = utils.load_fund_list()

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

for fund in fund_list:
    if fund.type != const.KEYWORD_MIX and fund.type != const.KEYWORD_STOCK: continue

    funds = session.query(Fund).filter(Fund.code == fund.code).all()
    if len(funds) != 1: continue




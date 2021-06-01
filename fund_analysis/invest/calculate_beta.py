"""
博迪投资学实践
"""

import pandas as pd

from fund_analysis import const

"""
This is a automatic investment analysis

"""
import argparse
from fund_analysis.const import COL_DAILY_RATE
from fund_analysis.tools import utils, data_utils
import logging

logger = logging.getLogger(__name__)


def main(code, index_name):
    if code:
        return calculate(code,index_name)

    fund_list = data_utils.load_fund_list()
    for fund in fund_list:
        calculate(fund.code,index_name,fund.name)

def calculate(code,index_name,fund_name=None):

    # 加载基金数据
    fund_data = data_utils.load_fund_data(code)
    if fund_data is None:
        logger.warning("基金[%s]数据有问题，忽略它...",code)
        return -999

    fund_rate = fund_data[[const.COL_DAILY_RATE]]

    # 加载指数数据
    index_data = data_utils.load_index_data_by_name(index_name)
    index_rate = index_data[['rate']]

    # 加载无风险利率
    bond_rate = data_utils.load_bond_interest_data()/365

    logger.debug(">基金[%d]行，市场[%d]行，国债[%d]行",len(fund_rate),len(index_data),len(bond_rate))
    fund_extra_rate = fund_rate.iloc[:,0] - bond_rate.iloc[:,0]
    fund_extra_rate = fund_extra_rate.dropna()
    market_extra_rate = index_rate.iloc[:,0] - bond_rate.iloc[:,0]
    market_extra_rate = market_extra_rate.dropna()
    print(market_extra_rate)
    logger.debug("<基金[%d]行，市场[%d]行，国债[%d]行", len(fund_extra_rate), len(market_extra_rate), len(bond_rate))

    if len(fund_extra_rate)==0:
        logger.warning("过滤后剩余基金数据为0")
        return -999

    # assert len(fund_data)==len(index_data), "基金数据行数!=指数行数"+str(len(fund_data))+"/"+str(len(index_data))
    # 用concat做表连接，key是index（日期）
    result = data_utils.merge_by_date([fund_extra_rate, market_extra_rate],
                                      new_col_names=[code,index_name])
    if len(result)==0:
        return -999

    fund_var, index_var = result.var()
    fund_index_cov = result.cov().iloc[0, 1]
    beta = fund_index_cov / index_var

    logger.debug('基金数量：%d天', len(result))
    logger.debug("指数名称：%s", index_name)
    logger.debug('指数方差：%.4f%%', index_var*100)
    if fund_name:
        logger.debug('基金名称：%s', fund_name)
    logger.debug('基金代码：%s', code)
    logger.debug('基金方差：%.4f%%', fund_var*100)
    logger.debug('Beta  值：%.4f', beta)
    return beta,result


# python -m fund_analysis.invest.calculate_beta --code 519778 --index 上证指数
# python -m fund_analysis.invest.calculate_beta --index 上证指数
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str, default=None)
    parser.add_argument('--index', '-n', type=str)
    args = parser.parse_args()

    utils.init_logger()
    logging.getLogger('matplotlib.font_manager').disabled = True
    main(args.code, args.index)

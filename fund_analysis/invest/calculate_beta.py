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
    fund_data = fund_data[[COL_DAILY_RATE]]
    fund_data.columns = [code]

    # 加载指数数据
    index_data = data_utils.load_index_data_by_name(index_name)
    index_data = data_utils.calculate_rate(index_data, 'close') # 转化成收益率
    index_data = index_data[['rate']] # 只取1列数据:rate
    index_data.columns = [index_name] # rename一下列名

    # assert len(fund_data)==len(index_data), "基金数据行数!=指数行数"+str(len(fund_data))+"/"+str(len(index_data))
    # 用concat做表连接，key是index（日期）
    result = pd.concat([fund_data, index_data], axis=1)
    result = result.dropna(how="any", axis=0)

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
    logger.debug('Beta  值：%.4f%%', beta*100)
    return beta


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

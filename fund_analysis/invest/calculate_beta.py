"""
博迪投资学实践
"""

import pandas as pd

"""
This is a automatic investment analysis

"""
import argparse
from fund_analysis.const import COL_DAILY_RATE
from fund_analysis.tools import utils, data_utils
import logging

logger = logging.getLogger(__name__)


def main(code, index_name):
    fund_data = data_utils.load_fund_data(code)
    fund_data = fund_data[[COL_DAILY_RATE]]
    fund_data.columns = [code]

    index_data = data_utils.load_index_data_by_name(index_name)
    index_data = data_utils.calculate_rate(index_data, 'close')
    index_data = index_data[['rate']]
    index_data.columns = [index_name]

    result = pd.concat([fund_data, index_data], axis=1)
    result = result.dropna(how="any", axis=0)

    fund_var, index_var = result.var()
    fund_index_cov = result.cov().iloc[0, 1]
    beta = fund_index_cov / index_var

    logger.debug("=============================================")
    logger.debug('数    量：%d天', len(result))
    logger.debug("指    数：%s", index_name)
    logger.debug('指数方差：%.2f', index_var)
    logger.debug('基    金：%s', code)
    logger.debug('基金方差：%.2f', fund_var)
    logger.debug('Beta  值：%.2f', beta)
    logger.debug("=============================================")


# python -m fund_analysis.invest.calculate_beta --code 519778 --index 上证指数
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str, default=None)
    parser.add_argument('--index', '-n', type=str)
    args = parser.parse_args()

    utils.init_logger()
    logging.getLogger('matplotlib.font_manager').disabled = True
    main(args.code, args.index)

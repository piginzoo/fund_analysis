import argparse
import logging

from fund_analysis import const
from fund_analysis.const import COL_DAILY_RATE, COL_RATE, COL_ACCUMULATIVE_NET
from fund_analysis.projects import cov_calculator
from fund_analysis.tools import data_utils, utils
from fund_analysis.tools.data_utils import calculate_rate

logger = logging.getLogger(__name__)


def calculate(fund_data_list, fund_list):
    sp500_index_data = data_utils.load_index_data_by_name('标普500')

    # 计算他们之间的相关系数
    cov_calculator.calculate(fund_data_list)

    # 计算和标普500之间的相关系数
    for fund_data, fund in zip(fund_data_list, fund_list):
        merge_dataframe = data_utils.merge_by_date([fund_data, sp500_index_data], [COL_ACCUMULATIVE_NET, 'sp500'])
        coef_value = merge_dataframe.corr().iloc[0, 1]
        logger.info("基金[%s](%s)和标普500的相关系数：%.2f", fund.code, fund.name, coef_value)


def main(args):
    codes = args.codes.split(",")
    fund_list = [data_utils.load_fund(code) for code in codes]
    fund_data_list = [data_utils.load_fund_data(code) for code in codes]
    calculate(fund_data_list, fund_list)

# python -m fund_analysis.projects.etf_sp500_compare --codes 003718,050025
if __name__ == '__main__':
    utils.init_logger(logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--codes', '-c', type=str, default=None)
    args = parser.parse_args()

    main(args)

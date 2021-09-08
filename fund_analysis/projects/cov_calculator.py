import logging

import numpy as np

from fund_analysis.const import COL_ACCUMULATIVE_NET
from fund_analysis.tools import data_utils, utils

logger = logging.getLogger(__name__)


def calculate(data, start_date=None):
    """
    自己实现一个协方差矩阵的计算，为何不用numpy或者pandas的？
    原因是，不同基金的日期无法对其，只能自己手工一对对的计算，
    然后在拼成一个矩阵了。
    只能两两之间可以做日期对其，可能存在不同的协方差的基准，
    也就是日期不一致的时候，没办法，也只能这样了。

    另外，可以指定截止日期，因为可能我不关心太久之前的数据，只关心3年内啥的
    """
    cov_maxtrix = np.zeros((len(data), len(data)))
    for i, fund1 in enumerate(data[:-1]):
        cov_maxtrix[i, i] = 1
        for j, fund2 in enumerate(data[i + 1:]):
            if start_date:
                fund1 = fund1.loc[start_date:]
                fund2 = fund2.loc[start_date:]
            result = data_utils.merge_by_date([fund1, fund2],
                                              selected_col_names=[COL_ACCUMULATIVE_NET, COL_ACCUMULATIVE_NET])
            cov = result.corr().iloc[0, 1]
            cov_maxtrix[i, i + j + 1] = cov
            logger.debug("相关系数=%.2f", cov)
    print(cov_maxtrix)


def main(fund_list, start=None):
    funds = [data_utils.load_fund_data(f) for f in fund_list]
    calculate(funds, start)


# python -m fund_analysis.projects.cov_calculator
if __name__ == '__main__':
    utils.init_logger()
    fund_list = ['005267', '002808', '166002',
                 '260108']  # , '519736', '007119', '110022', '163412', '003396', '006228']
    main(fund_list)  # ,'2019-01-01')

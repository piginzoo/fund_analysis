'''
测试统计内容
'''

import logging

import scipy.stats as stats

from fund_analysis import const
from fund_analysis.tools import data_utils, utils

logger = logging.getLogger(__name__)


def test_shapiro_test():
    """
    https://zhuanlan.zhihu.com/p/26539771
    https://www.jianshu.com/p/e202069489a6
    测试是不是符合正太分布
    """
    data = data_utils.load_fund_data('519778')
    W,p_value = stats.shapiro(data[const.COL_DAILY_RATE])
    # p_value
    if p_value < 0.05:
        logger.debug("p=%.2f，不是正态分布",p_value)
    else:
        logger.debug("p=%.2f，不是正态分布",p_value)

# python -m test.test_stat
if __name__ == '__main__':
    utils.init_logger()
    test_shapiro_test()

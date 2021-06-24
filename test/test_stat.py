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
    data = data_utils.load_fund_data('519778').iloc[0:50]
    W,p_value = stats.shapiro(data[const.COL_DAILY_RATE])
    # p_value
    if p_value < 0.05:
        logger.debug("W=%.2f,p=%.2f，拒绝原假设(是正态分布)，不是正态分布",W,p_value)
    else:
        logger.debug("W=%.2f,p=%.2f，接受原假设(正态分布)，是正态分布",W,p_value)

def test_KS_test():
    """
    https://www.cnblogs.com/eat-drink-breathe-hard/p/13798547.html

    As Stijn pointed out, the k-s test returns a D statistic and a p-value corresponding to the D statistic.
    The D statistic is the absolute max distance (supremum) between the CDFs of the two samples.
    The closer this number is to 0 the more likely it is that the two samples were drawn from the same distribution.
    Check out the Wikipedia page for the k-s test.
    It provides a good explanation: https://en.m.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test

    The p-value returned by the k-s test has the same interpretation as other p-values.
    You reject the null hypothesis that the two samples were drawn from the same distribution
    if the p-value is less than your significance level.
    You can find tables online for the conversion of the D statistic into a p-value if you are interested in the procedure.
    """
    data = data_utils.load_fund_data('519778')
    data = data[[const.COL_DAILY_RATE]]
    data = data.dropna()
    test_stat = stats.kstest(data,'norm',args=(data.mean(),data.std()))
    logger.debug("KS检验结果：%r",test_stat)
    if test_stat.pvalue < 0.05:
        logger.debug("KS检验%d条数据，p=%.2f<0.05，拒绝原假设(是正态分布)，不是正态分布",len(data),test_stat.pvalue)
    else:
        logger.debug("KS检验%d条数据，p=%.2f>0.05，不拒绝原假设(是正态分布)，应该是正态分布",len(data),test_stat.pvalue)


# python -m test.test_stat
if __name__ == '__main__':
    utils.init_logger()
    test_shapiro_test()
    test_KS_test()

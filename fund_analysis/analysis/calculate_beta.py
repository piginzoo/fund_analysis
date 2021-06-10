"""
博迪投资学实践
"""
import warnings,logging
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", module="matplotlib")
logging.getLogger('matplotlib').disabled = True

import statsmodels.api as sm
from pandas import Series
import matplotlib.pyplot as plt
from fund_analysis import const
from fund_analysis.const import PERIOD_NUM
from fund_analysis.tools.data_utils import calculate_rate



"""
This is a automatic investment analysis

"""
import argparse
from fund_analysis.tools import utils, data_utils
import logging

logger = logging.getLogger(__name__)


def main(code, type, period, index_name):
    if code:
        calculate_by_cov(code, type, period, index_name)
        calculate_by_OLS(code, type, period, index_name)
    else:
        fund_list = data_utils.load_fund_list()
        for fund in fund_list:
            calculate_by_cov(fund.code, type, period, index_name)
            calculate_by_OLS(fund.code, type, period, index_name)


def load_data(code, type, period, index_name):
    """
    按照周期加载三类数据：基金/股票；指数（市场）；国债（无风险）
    :param code: 代码
    :param type: stock|fund
    :param period: 期间：day,week,month,year
    :param index_name:指数名称，中文的
    :return:
    """
    # 加载基金/股票数据
    if type == const.FUND:
        data = data_utils.load_fund_data(code)
        if data is None:
            logger.warning("[%s]数据有问题，忽略它...", code)
            return -999, None, None
        data_rate = calculate_rate(data, const.COL_ACCUMULATIVE_NET, period, 'price')
    elif type == const.STOCK:
        data = data_utils.load_stock_data(code)
        data_rate = calculate_rate(data, 'close', period, 'price')
    else:
        raise ValueError("type不合法：" + type)

    # 加载指数数据
    index_data = data_utils.load_index_data_by_name(index_name, period)
    index_rate = index_data[['rate']]

    # 加载无风险利率(/365=每天利率）
    bond_rate = data_utils.load_bond_interest_data() / PERIOD_NUM[period]
    bond_rate = calculate_rate(bond_rate, '收盘', period, 'rate')

    return data_rate, index_rate, bond_rate


def calculate_by_cov(code, type, period, index_name):
    r_i, r_m, r_f = load_data(code, type, period, index_name)

    logger.debug(">基金/股票[%d]行，指数（市场）[%d]行，国债（无风险）[%d]行", len(r_i), len(r_m), len(r_f))

    # assert len(fund_data)==len(index_data), "基金/股票数据行数!=指数行数"+str(len(fund_data))+"/"+str(len(index_data))
    # 用concat做表连接，key是index（日期）
    result = data_utils.merge_by_date([r_i, r_m],
                                      new_col_names=[code, index_name])
    if len(result) == 0:
        return -999, None

    fund_var, index_var = result.var()
    fund_std, index_std = result.std()
    fund_index_cov = result.cov().iloc[0, 1]
    beta = fund_index_cov / index_var

    logger.debug('股基时间\t：%d天', len(result))
    logger.debug("指数名称\t：%s", index_name)
    logger.debug('指标准差\t：%.4f%%', index_std)
    logger.debug('股基代码\t：%s', code)
    logger.debug('基标准差\t：%.4f%%', fund_std)
    logger.debug('Beta  值\t：%.4f', beta)
    return beta, result


def calculate_by_OLS(code, data_type, period, index_name):
    """
    r_i = r_f  + beta ( r_m - r_f )
    :param code:
    :param data_type:
    :param period:
    :param index_name:
    :return:
    """

    r_i, r_m, r_f = load_data(code, data_type, period, index_name)
    logger.debug("预处理前:基金/股票[%d]行，指数（市场）[%d]行，国债（无风险）[%d]行", len(r_i), len(r_m), len(r_f))

    y = r_i  # 因变量 fund_rate
    x = r_m  # 自变量 r_m

    x = x.iloc[:, 0] - r_f.iloc[:, 0]  # X:r_m - r_f,注意，不能直接减，因为列名不一致，要通过".iloc[:, 0]"转成series
    x = x.dropna()

    def join(df1, df2):
        if type(df1) == Series: df1 = df1.to_frame()
        if type(df2) == Series: df2 = df2.to_frame()
        df12 = df1.join(df2, how="inner", lsuffix="d_")
        return df12.iloc[:, 0], df12.iloc[:, 1]

    x, y = join(x, y)

    logger.debug("预处理后:市场收益[%d]条, 基金/股票收益[%d]条，", len(x), len(y))

    # logger.debug("预处理后基金/股票收益[%d]条，市场收益[%d]条", len(x), len(y))

    x = sm.add_constant(x)  # 若模型中有截距，必须有这一步

    model = sm.OLS(y, x).fit()  # 构建最小二乘模型并拟合
    logger.debug(model.summary(xname=['无风险利率', 'Beta贝塔值']))  # 输出回归结果
    predicts = model.predict()
    # plot(x, y, predicts)

    regression_r_f, regression_beta = model.params
    logger.debug("二元回归计算出来的贝塔：%.4f", regression_beta)
    logger.debug("二元回归计算无风险利率：%.4f", regression_r_f)
    logger.debug("国债利率（无风险利率）：%.4f", r_f.mean().values[0])



# python -m fund_analysis.analysis.calculate_beta --code 519778 --type fund --period week --index 上证指数
# python -m fund_analysis.analysis.calculate_beta --index 上证指数
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str, default=None)
    parser.add_argument('--type', '-t', type=str, default=None)  #
    parser.add_argument('--index', '-n', type=str)
    parser.add_argument('--period', '-p', type=str)
    args = parser.parse_args()

    utils.init_logger()
    logging.getLogger('matplotlib.font_manager').disabled = True
    main(args.code, args.type, args.period, args.index)

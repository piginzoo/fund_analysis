"""
参考：
- https://blog.csdn.net/robert_chen1988/article/details/103551261
- https://zhuanlan.zhihu.com/p/54129885
- https://blog.csdn.net/BF02jgtRS00XKtCx/article/details/108687817 OLS结果字段解释
"""
import argparse
import logging
import warnings
from collections import namedtuple

import matplotlib.pyplot as plt
import statsmodels.api as sm

from fund_analysis.invest import calculate_beta
from fund_analysis.tools import utils, data_utils
from fund_analysis import const

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", module="matplotlib")
logging.getLogger('matplotlib.font_manager').disabled = True
logging.getLogger('matplotlib').disabled = True

logger = logging.getLogger(__name__)

Result = namedtuple('Result', ['beta', 'result'])


PERIOD_NUM={
    const.PERIOD_DAY:365,
    const.PERIOD_WEEK: 52,
    const.PERIOD_MONTH: 12,
    const.PERIOD_YEAR: 1,

}

def main(args, group_num=3, num_inside_group=3):
    start, code, type, period = args.start, args.code, args.type,args.period

    # 加载无风险利率(/365=每天利率）
    bond_rate = data_utils.load_bond_interest_data() / PERIOD_NUM[period]

    beta, result = calculate_beta.calculate_by_cov(code, type, period, '上证指数')

    logger.debug("基金/股票 和 指数 的信息:")
    logger.debug("=======================")
    logger.debug("\n%r", result.describe())
    logger.debug("=======================")

    # 虽然上面已经计算出来了beta，但那个是根据CAPM模型计算出来的，即 Cov(市场和基金协方差)/市场方差
    # 现在，我们用纯数据来回归出来beta
    # r_i = r_f + \beta * ( r_m - r_f )
    # Y   = C1  + C2    *     X
    # 我们来多元回归出来C1和C2，
    # 如果CAPM成立，那么C1就应该约等于r_f，C2约等于r_m - r_f
    # logger.debug("%s beta = %.3f", fund.code, beta)

    y = result.iloc[:, 0]  # 因变量 fund_rate
    x = result.iloc[:, 1]  # 自变量 r_m
    logger.debug("预处理前基金收益[%d]条，市场收益[%d]条", len(x), len(y))
    x = x - bond_rate.iloc[:, 0]  # X:r_m - r_f,注意，不能直接减，因为列名不一致，要转成series
    x = x.dropna()
    y = y.loc[x.index]  # 怕日期有遗漏，再反向过滤一遍fund_rate
    logger.debug("预处理后基金收益[%d]条，市场收益[%d]条", len(x), len(y))

    x = sm.add_constant(x)  # 若模型中有截距，必须有这一步
    model = sm.OLS(y, x).fit()  # 构建最小二乘模型并拟合
    logger.debug(model.summary())  # 输出回归结果
    predicts = model.predict()
    # plot(x, y, predicts)

    regression_r_f, regression_beta = model.params
    logger.debug("根据贝塔定义计算出来的Beta：%.4f", beta)
    logger.debug("根据二元回归计算出来的Beta：%.4f", regression_beta)
    logger.debug("无风险利率平均值：%.4f", bond_rate.mean().values[0])
    logger.debug("二元回归计算无风：%.4f", regression_r_f)


# def main(args,group_num=3, num_inside_group=3):
#     start, code, type = args.start, args.code, args.type
#
#     funds = data_utils.load_fund_list_from_db()
#
#     random.shuffle(funds)
#
#     results = []
#     counter = 0
#     total = num_inside_group * group_num
#
#     # 加载无风险利率(/365=每天利率）
#     bond_rate = data_utils.load_bond_interest_data() / 365
#
#     for fund in funds:
#
#         if counter > total: break
#         if fund.start_date > date_utils.str2date(start):
#             logger.debug("%r>%r", fund.start_date, start)
#             continue
#
#         beta, result = calculate_beta.calculate(fund.code, '上证指数', fund.name)
#
#         if result is None: continue
#
#         logger.debug("基金 和 指数 的信息:")
#         logger.debug("=======================")
#         logger.debug("\n%r", result.describe())
#         logger.debug("=======================")
#
#         # 虽然上面已经计算出来了beta，但那个是根据CAPM模型计算出来的，即 Cov(市场和基金协方差)/市场方差
#         # 现在，我们用纯数据来回归出来beta
#         # r_i = r_f + \beta * ( r_m - r_f )
#         # Y   = C1  + C2    *     X
#         # 我们来多元回归出来C1和C2，
#         # 如果CAPM成立，那么C1就应该约等于r_f，C2约等于r_m - r_f
#         # logger.debug("%s beta = %.3f", fund.code, beta)
#
#         y = result.iloc[:, 0]  # 因变量 fund_rate
#         x = result.iloc[:, 1]  # 自变量 r_m
#         logger.debug("预处理前基金收益[%d]条，市场收益[%d]条", len(x), len(y))
#         x = x - bond_rate.iloc[:,0] # X:r_m - r_f,注意，不能直接减，因为列名不一致，要转成series
#         x = x.dropna()
#         y = y.loc[x.index]     # 怕日期有遗漏，再反向过滤一遍fund_rate
#         logger.debug("预处理后基金收益[%d]条，市场收益[%d]条", len(x), len(y))
#
#         x = sm.add_constant(x)  # 若模型中有截距，必须有这一步
#         model = sm.OLS(y, x).fit()  # 构建最小二乘模型并拟合
#         logger.debug(model.summary())  # 输出回归结果
#         predicts = model.predict()
#         # plot(x, y, predicts)
#
#         regression_r_f, regression_beta = model.params
#         logger.debug("根据贝塔定义计算出来的Beta：%.4f" , beta)
#         logger.debug("根据二元回归计算出来的Beta：%.4f", regression_beta)
#         logger.debug("无风险利率平均值：%.4f", bond_rate.mean().values[0])
#         logger.debug("二元回归计算无风：%.4f", regression_r_f)
#
#         logger.debug(
#             "--------------------------------------------------------------------------------------------------------------------------------------------")
#         results.append(Result(beta, result))
#         counter += 1
#         break
#
#     results = sorted(results, reverse=True, key=lambda re: re.beta)
#
#     results_by_group = [results[x:x + num_inside_group] for x in range(0, len(results), num_inside_group)]
#     # print(results_by_group)


def plot(x, y, pred):
    # 真实值与预测值的关系# 设置绘图风格
    plt.style.use('ggplot')

    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 指定默认字体

    # 散点图
    # print(x,y)
    # print(len(x),len(y))
    _max = max(x.max(), y.max())
    _min = max(x.min(), y.min())
    plt.xlim(_min, _max)
    plt.ylim(_min, _max)
    plt.scatter(x, y, label='观测点')

    # 回归线
    plt.plot(x, pred, 'r--', lw=2, label='拟合线')

    # 添加轴标签和标题
    plt.title('Beta回归')
    plt.xlabel('股指超额收益%')
    plt.ylabel('基金超额收益%')

    # 去除图边框的顶部刻度和右边刻度
    plt.tick_params(top='off', right='off')
    # 添加图例
    plt.legend(loc='upper left')
    # 图形展现
    plt.show()


# python -m test.test_capm --start 2018-1-1 --code 300122 --type stock --period week
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', '-s', type=str, default=None)
    parser.add_argument('--code', '-c', type=str, default=None)
    parser.add_argument('--type', '-t', type=str, default=None)
    parser.add_argument('--period', '-p', type=str, default='week')
    args = parser.parse_args()
    utils.init_logger()
    main(args)

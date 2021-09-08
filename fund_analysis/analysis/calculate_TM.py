"""

r_p=r_f+ \beta1 (r_M-r_f)+\beta2 (r_M-r_f)^2 + \alpha_p + \epsilon_i

Treynor-Mazuy 模型

基金的收益分解成四部分:
1. 无风险利率 rf
2. 战略资产配置收益(承受市场系统性风险带来的收益)𝛃1
3. 战术资产配置收益(市场择时带来的收益)𝛃2
4. 选股带来的收益𝛂
模型缺点:
1. 择时beta为什么是(Rm-Rf)的线性形式?能否放松函数形式限制?
2. 如何选取合适的回归数据周期
3. 历史不代表未来，例如beta随时间变化

OLS解决高次因变量拟合：https://zhuanlan.zhihu.com/p/22692029
虽然 X 和 Y 的关系不是线性的，但是 Y 和 [X^1, X^2,....] 的关系是高元线性的。
也就是说，只要我们把高次项当做其他的自变量[X_1, X_2,....]
"""
import logging
import warnings

from fund_analysis.analysis.base_calculator import BaseCalculator

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", module="matplotlib")
logging.getLogger('matplotlib').disabled = True
from fund_analysis import const
from fund_analysis.const import PERIOD_NUM
from fund_analysis.tools.data_utils import calculate_rate, join
import statsmodels.api as sm
import matplotlib.pyplot as plt
import numpy as np
import argparse
from fund_analysis.tools import data_utils
import logging

logger = logging.getLogger(__name__)


class TMCalculater(BaseCalculator):

    def name(self):
        return "Alpha:计算股票/基金的alpha"

    def load_data(self, args):
        """
        按照周期加载三类数据：基金/股票；指数（市场）；国债（无风险）
        :param code: 代码
        :param type: stock|fund
        :param period: 期间：day,week,month,year
        :param index_name:指数名称，中文的
        :return:
        """

        code, type, period, index_name = args.code, args.type, args.period, args.index

        # 加载基金/股票数据
        if type == const.FUND:
            data = data_utils.load_fund_data(code)
            if data is None:
                logger.warning("[%s]数据有问题，忽略它...", code)
                raise ValueError("加载数据失败了：" + code)
            data_rate = calculate_rate(data, const.COL_ACCUMULATIVE_NET, period, 'price')
        elif type == const.STOCK:
            data = data_utils.load_stock_data(code)
            data_rate = calculate_rate(data, 'close', period, 'price')
        else:
            raise ValueError("类型不合法：必须为stock或fund" + type)

        # 加载指数数据
        index_data = data_utils.load_index_data_by_name(index_name, period)
        index_rate = data_utils.calculate_rate(index_data, 'close', period)

        # 加载无风险利率(/365=每天利率）
        bond_rate = data_utils.load_bond_interest_data() / PERIOD_NUM[period]

        # 需要平均一下利率，calulate_by='rate'
        bond_rate = calculate_rate(bond_rate, '收盘', period, calulate_by='rate')

        return data_rate, index_rate, bond_rate

    def calculate(self, data):
        """
        r_p - r_f = \beta1 (r_M-r_f) + \beta2 (r_M-r_f)^2 + \alpha_p + \epsilon_i
        ---  ----   ~~~~~  ----------- ~~~~~~ -----------   ~~~~~~~~   -----------
            Y                  X                 X^2
        利率   无风   β1                  β2                    α          残差
        已知   已知   待估计     已知       待估计      已知      待估计        无需计算

        实现参考：https://zhuanlan.zhihu.com/p/22692029
        实现思路：把高次项当做一个因变量而已，这样就变成标准的一次的OLS了，
                只不过输入的时候，x1=x；然后，把x平方一下，作为x2,
                然后式子就变成了：
                Y= alpha + beta1 * x1 + beta2 * x2
        """

        r_i, r_m, r_f = data
        logger.debug("预处理前:基金/股票[%d]行，指数（市场）[%d]行，国债（无风险）[%d]行", len(r_i), len(r_m), len(r_f))

        y = r_i.iloc[:, 0] - r_f.iloc[:, 0]
        y = y.dropna()

        # 会按照日期自动相减，日期对不上的为nan
        x = r_m.iloc[:, 0] - r_f.iloc[:, 0]
        x = x.dropna()
        x, y = join(x, y)

        logger.debug("预处理后:市场收益[%d]条, 基金/股票收益[%d]条，", len(x), len(y))

        new_x = np.column_stack((x, x ** 2))  # 把一维变成二维，二维是原值的平方：x1[1,2,3] => x1,x2 [[1,1],[2,4],[3,9]]
        x_with_const = sm.add_constant(new_x)  # 若模型中有截距alpha，必须有这一步
        model = sm.OLS(y, x_with_const).fit()  # 构建最小二乘模型并拟合

        logger.debug(model.summary(xname=['Alhpa', 'Beta1', 'Beta2']))  # 输出回归结果
        predicts = model.predict()
        alhpa, beta1, beta2 = model.params
        logger.debug("选股能力Alpha：%.4f", alhpa)
        logger.debug("系统风险Beta1：%.4f", beta1)
        logger.debug("择时能力Beta2：%.4f", beta2)

        return x, y, predicts, alhpa, beta1, beta2

    def plot(self, data):

        # logger.debug("PLOT数据：%r",data)
        x, y, pred, alhpa, beta1, beta2 = data
        # 真实值与预测值的关系# 设置绘图风格
        plt.style.use('ggplot')

        plt.rcParams['font.sans-serif'] = ['SimSun']  # 指定默认字体

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

        return plt

    def get_arg_parser(self):
        parser = argparse.ArgumentParser(description='''
        计算一个基金的TM模型值，用于评价基金的择时和选股能力
        ''')
        parser.add_argument('--code', '-c', type=str, default=None, help='代码')
        parser.add_argument('--type', '-t', type=str, default=None, help='类型：fund|stock')
        parser.add_argument('--index', '-n', type=str, help='指数名称：上证指数|深成指数')
        parser.add_argument('--period', '-p', type=str, help='周期：day|week|month|year')
        return parser


# python -m fund_analysis.analysis.calculate_TM --code 001319 --type fund --period week --index 上证指数
if __name__ == '__main__':
    calculator = TMCalculater()
    calculator.main(args=None, console=True)

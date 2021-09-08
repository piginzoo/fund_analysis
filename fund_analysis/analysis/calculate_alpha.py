"""
博迪投资学实践
计算Alpha，基于Jensen Alpha公式
r_i - r_f = alpha_i + beta_i(r_m - r_f) + epsilon_i
利率   无风   α        β      市场   无风    残差
已知   已知   待估计    待估计  已知   已知    无需计算

"""
import logging
import warnings

from fund_analysis.analysis.base_calculator import BaseCalculator
from fund_analysis.tools.utils import export_matplotlib_image_2_base64

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", module="matplotlib")
logging.getLogger('matplotlib').disabled = True
from fund_analysis import const
from fund_analysis.const import PERIOD_NUM
from fund_analysis.tools.data_utils import calculate_rate, join
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib

"""
This is a automatic investment analysis

"""
import argparse
from fund_analysis.tools import utils, data_utils
import logging

logger = logging.getLogger(__name__)


class AlphaCalculater(BaseCalculator):

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
        index_rate = data_utils.calculate_rate(index_data,'close',period)

        # 加载无风险利率(/365=每天利率）
        bond_rate = data_utils.load_bond_interest_data() / PERIOD_NUM[period]
        bond_rate = calculate_rate(bond_rate, '收盘', period)

        return data_rate, index_rate, bond_rate

    def calculate(self, data):
        """
        r_i - r_f = alpha_i + beta_i(r_m - r_f) + epsilon_i
        ---------                   -----------
            Y                           X
        利率   无风   α        β      市场   无风    残差
        已知   已知   待估计    待估计  已知   已知    无需计算

        :param code:
        :param data_type:
        :param period:
        :param index_name:
        :return:
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

        x_with_const = sm.add_constant(x)  # 若模型中有截距，必须有这一步

        model = sm.OLS(y, x_with_const).fit()  # 构建最小二乘模型并拟合
        logger.debug(model.summary(xname=['Alhpa', 'Beta']))  # 输出回归结果
        predicts = model.predict()
        regression_alhpa, regression_beta = model.params
        logger.debug("二元回归计算无风险Alpha：%.4f", regression_alhpa)
        logger.debug("二元回归计算出来的Beta：%.4f", regression_beta)

        return x, y, predicts

    def plot(self, data):

        # logger.debug("PLOT数据：%r",data)
        x, y, pred = data
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
        计算一个股票、基金的Alpha值，
        需要提供市场参考指数名称、资产类型（股票还是基金）、和计算使用周期（日、周、月、年）
        ''')
        parser.add_argument('--code', '-c', type=str, default=None, help='代码')
        parser.add_argument('--type', '-t', type=str, default=None, help='类型：fund|stock')
        parser.add_argument('--index', '-n', type=str, help='指数名称：上证指数|深成指数')
        parser.add_argument('--period', '-p', type=str, help='周期：day|week|month|year')
        return parser


# python -m fund_analysis.analysis.calculate_alpha --code 001319 --type fund --period week --index 上证指数
if __name__ == '__main__':
    calculator = AlphaCalculater()
    calculator.main(args=None,console=True)

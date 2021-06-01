"""
参考：
- https://blog.csdn.net/robert_chen1988/article/details/103551261
- https://zhuanlan.zhihu.com/p/54129885
- https://blog.csdn.net/BF02jgtRS00XKtCx/article/details/108687817 OLS结果字段解释
"""
import argparse
import logging
import random
import warnings
import matplotlib
import statsmodels.api as sm
import matplotlib.pyplot as plt
from fund_analysis.tools import utils, data_utils
from fund_analysis.invest import calculate_beta

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", module="matplotlib")
logging.getLogger('matplotlib.font_manager').disabled = True
logging.getLogger('matplotlib').disabled = True

logger = logging.getLogger(__name__)


def main():
    funds = data_utils.load_fund_list()

    random.shuffle(funds)
    funds = funds[:100]

    for fund in funds:
        beta,result = calculate_beta.calculate(fund.code,'上证指数',fund.name)

        # r_i = r_f+\beta (R_m-r_f)
        # r_i = r_f + \beta R_m

        # logger.debug("%s beta = %.3f", fund.code, beta)

        y = result.iloc[:, 0]  # 因变量code
        x = result.iloc[:, 1]   # 自变量为市场r_m
        # x = sm.add_constant(x)  # 若模型中有截距，必须有这一步
        model = sm.OLS(y, x).fit()  # 构建最小二乘模型并拟合
        logger.debug(model.summary())  # 输出回归结果
        predicts = model.predict()
        plot(x,y,predicts)

        logger.debug("-----------------------------------")
        break

def plot(x,y,pred):
    # 真实值与预测值的关系# 设置绘图风格
    plt.style.use('ggplot')

    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 指定默认字体

    # 散点图
    # print(x,y)
    # print(len(x),len(y))
    plt.scatter(x, y, label='观测点')

    # 回归线
    plt.plot(x, pred, 'r--', lw=2, label='拟合线')

    # 添加轴标签和标题
    plt.title('真实值VS.预测值')
    plt.xlabel('真实值')
    plt.ylabel('预测值')

    # 去除图边框的顶部刻度和右边刻度
    plt.tick_params(top='off', right='off')
    # 添加图例
    plt.legend(loc='upper left')
    # 图形展现
    plt.show()

# python -m test.test_capm
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    utils.init_logger()
    main()

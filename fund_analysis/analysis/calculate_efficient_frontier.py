"""
计算有效前沿
[https://zhuanlan.zhihu.com/p/50329231](https://zhuanlan.zhihu.com/p/50329231)
[https://www.zhihu.com/question/36388336](https://www.zhihu.com/question/36388336)
"""
import warnings

from fund_analysis.tools import plot_utils

warnings.filterwarnings("ignore", category=UserWarning)

import argparse
import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 通过Monte Carlo模拟产生有效前沿组合
from fund_analysis.const import COL_DAILY_RATE
from fund_analysis.tools import utils, data_utils

def calculate(data, portfolio_num):
    data_cov = data.cov()

    port_returns = []
    port_volatility = []
    sharpe_ratio = []
    stock_weights = []

    num_assets_num = len(data.columns)

    np.random.seed(101)

    for single_portfolio in range(portfolio_num):
        weights = np.random.random(num_assets_num)
        weights /= np.sum(weights)
        returns = np.dot(weights, data.mean())
        volatility = np.sqrt(np.dot(weights.T, np.dot(data_cov, weights)))
        sharpe = returns / volatility
        sharpe_ratio.append(sharpe)
        port_returns.append(returns)
        port_volatility.append(volatility)
        stock_weights.append(weights)

    portfolio = {'Returns': port_returns,
                 'Volatility': port_volatility,
                 'Sharpe Ratio': sharpe_ratio}

    for counter, symbol in enumerate(data):
        portfolio[symbol + ' Weight'] = [Weight[counter] for Weight in stock_weights]

    df = pd.DataFrame(portfolio)
    column_order = ['Returns', 'Volatility', 'Sharpe Ratio'] + [stock + ' Weight' for stock in data]
    df = df[column_order]
    df.head()
    return df


def show(df):#,df_list):

    # plt.subplot(121)
    plt.style.use('ggplot')
    df.plot.scatter(x='Volatility',
                    y='Returns',
                    c='Sharpe Ratio',
                    cmap='autumn',
                    edgecolors='black',
                    figsize=(15, 9),
                    grid=True)
    plt.xlabel('Volatility (Std. Deviation)')
    plt.ylabel('Expected Returns')
    plt.title('Efficient Frontier')

    # plt.subplot(122)
    # for df in df_list:
    #     plot_utils.show_plot(x_data=df.index,
    #                          y_data=df.)

    plt.show()


def main(args):
    codes = args.codes.split(",")
    data_list = [data_utils.load_fund_data(code) for code in codes]
    data = data_utils.merge_by_date(data_list,
                                    [COL_DAILY_RATE]*len(data_list),
                                    codes)
    calculated_data = calculate(data,args.sample)
    show(calculated_data)

"""
python -m fund_analysis.analysis.calculate_efficient_frontier \
--code 519778,000960,151002,162201,180001,040001  \
--sample 1000
"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--codes', '-c', type=str, default=None)
    parser.add_argument('--file', '-f', type=str, default=None)
    parser.add_argument('--sample', '-s', type=int, default=1000)
    args = parser.parse_args()

    utils.init_logger(logging.DEBUG)
    logging.getLogger('matplotlib.font_manager').disabled = True
    logging.getLogger('matplotlib.colorbar').disabled = True
    main(args)

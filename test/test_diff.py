"""
计算差分（一阶导）、二阶差分（二阶导）

matplot color: https://matplotlib.org/stable/tutorials/colors/colors.html

"""
import matplotlib.pyplot as plt
from pandas import DataFrame

from fund_analysis import const
from fund_analysis.tools import data_utils


def show_plot(x_data, y_data, color):
    ax1 = plt.gca()
    ax1.plot(x_data, y_data, color=color)
    # ax1.set_ylabel(y_label)
    ax1.legend(loc='upper left')
    # plt.title(tilte)
    plt.axhline(y=0, color='0.8', linestyle='-.')


def show(data1, data2, data3):
    # plt.subplot(311)
    show_plot(x_data=data1.index, y_data=data1, color='b')
    # plt.subplot(312)
    show_plot(x_data=data2.index, y_data=data2, color='r')
    # plt.subplot(313)
    show_plot(x_data=data3.index, y_data=data3, color='g')

    manager = plt.get_current_fig_manager()
    manager.window.state('zoomed')


# 单指数平滑,https://www.pythonf.cn/read/149498
def exponential_smoothing(df, alpha):
    """
        series - dataset with timestamps
        alpha - float [0.0, 1.0], smoothing parameter
    """

    # print("df.index[0]",df.index[0])
    # print("df.iloc[0]",df.iloc[0][const.COL_ACCUMULATIVE_NET])

    result = [[df.index[0], df.iloc[0][const.COL_ACCUMULATIVE_NET]]]
    for i in range(1, len(df)):
        date = df.index[i]
        value = df.iloc[i][const.COL_ACCUMULATIVE_NET]
        smooth_value = alpha * value + (1 - alpha) * result[i - 1][1]
        result.append([date, smooth_value])

    df = DataFrame(result, columns=['date', 'value'])
    df.set_index(['date'], inplace=True)
    return df


def main(code, threshold):
    data = data_utils.load_fund_data(code)
    data = data[[const.COL_ACCUMULATIVE_NET]]

    # data_mean = resample('1W', how='mean').fillna(0)

    exp_smooth_data = exponential_smoothing(data, alpha=0.1)
    show_plot(x_data=exp_smooth_data.index, y_data=exp_smooth_data, color='y')

    data_diff1 = exp_smooth_data.diff(1)
    data_diff2 = exp_smooth_data.diff(2)  # data_diff1.diff(1)
    show_plot(x_data=data.index, y_data=data, color='b')
    show_plot(x_data=data_diff1.index, y_data=data_diff1, color='r')
    show_plot(x_data=data_diff2.index, y_data=data_diff2, color='g')

    up = data_diff2[data_diff2['value'] > threshold]
    down = data_diff2[data_diff2['value'] < -threshold]

    ax1 = plt.gca()
    ax1.scatter(data.loc[up.index].index, data.loc[up.index], color='g')
    ax1.scatter(data.loc[down.index].index, data.loc[down.index], color='r')

    plt.show()


# python -m test.test_diff
if __name__ == '__main__':
    main(code='519778', threshold=0.05)

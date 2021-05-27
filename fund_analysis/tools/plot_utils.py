import logging
import warnings
logging.getLogger('matplotlib.font_manager').disabled = True
logging.getLogger('matplotlib').disabled = True

logger = logging.getLogger(__name__)


import matplotlib
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", module="matplotlib")

matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 指定默认字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题


def show_plot(x_data, y_data, x_label, y_label, tilte):
    ax1 = plt.gca()
    ax1.plot(x_data, y_data)
    ax1.set_ylabel(y_label)
    ax1.set_xlabel(x_label)
    ax1.legend(loc='upper left')

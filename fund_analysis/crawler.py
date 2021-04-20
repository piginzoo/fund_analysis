# 导入需要的模块
import argparse
import logging
import random
import time

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

from fund_analysis.conf import NUM_PER_PAGE
from fund_analysis.helper import get_start_end_date, get_page_num, get_content, save_data
from fund_analysis.utils import load_data,init_logger

logger = logging.getLogger(__name__)

# 指定默认字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family'] = 'sans-serif'
# 解决负号'-'显示为方块的问题
matplotlib.rcParams['axes.unicode_minus'] = False


# 从网页抓取数据
def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    # 获取表头
    heads = []
    for head in soup.findAll("th"):
        heads.append(head.contents[0])
    logger.debug("获得表头：%r", heads)

    # 数据存取列表
    records = []

    # 解析数据
    for row in soup.findAll("tbody")[0].findAll("tr"):
        row_records = []
        for record in row.findAll('td'):
            val = record.contents

            # 处理空值
            if not val:
                row_records.append(np.nan)
            else:
                row_records.append(val[0])

        # 记录数据
        records.append(row_records)

    # 数据整理到dataframe
    np_records = np.array(records)
    data = pd.DataFrame()
    for col, col_name in enumerate(heads):
        data[col_name] = np_records[:, col]

    return data


def main(code):
    total_data = load_data(code)

    start_date, end_date = get_start_end_date(code, total_data)

    logger.info("准备爬取 [%s] --> [%s] 的数据", start_date, end_date)

    page_num = get_page_num(code, start_date, end_date)

    for i in range(1, page_num + 1):

        html = get_content(code, i, NUM_PER_PAGE, start_date, end_date)

        data = parse_html(html)

        if data is None:
            continue

        # 修改数据类型
        data['净值日期'] = pd.to_datetime(data['净值日期'], format='%Y/%m/%d')
        data['单位净值'] = data['单位净值'].astype(float)
        data['累计净值'] = data['累计净值'].astype(float)
        data['日增长率'] = data['日增长率'].str.strip('%').astype(float)
        # 按照日期升序排序并重建索引
        data = data.sort_values(by='净值日期', axis=0, ascending=True).reset_index(drop=True)

        if total_data is None:
            total_data = data
            logger.debug("基金[%s]不存在，创建[%d]条", code, len(data))
        else:
            total_data = total_data.append(data)
            logger.debug("追加[%d]条到基金[%s]中，合计[%d]条",len(data),code,len(total_data))

        data_path = save_data(code, total_data)

        time.sleep(random.random() * 10)
        logger.info("已将第%d页数据保存到[%s]中，准备爬取第%d页", i, data_path, i + 1)


def show(data):
    # 获取净值日期、单位净值、累计净值、日增长率等数据并
    net_value_date = data['净值日期']
    net_asset_value = data['单位净值']
    accumulative_net_value = data['累计净值']
    daily_growth_rate = data['日增长率']

    # 作基金净值图
    fig = plt.figure()
    # 坐标轴1
    ax1 = fig.add_subplot(111)
    ax1.plot(net_value_date, net_asset_value)
    ax1.plot(net_value_date, accumulative_net_value)
    ax1.set_ylabel('净值数据')
    ax1.set_xlabel('日期')
    plt.legend(loc='upper left')
    # 坐标轴2
    ax2 = ax1.twinx()
    ax2.plot(net_value_date, daily_growth_rate, 'r')
    ax2.set_ylabel('日增长率（%）')
    plt.legend(loc='upper right')
    plt.title('基金净值数据')
    plt.show()

    # 绘制分红配送信息图
    bonus = accumulative_net_value - net_asset_value
    plt.figure()
    plt.plot(net_value_date, bonus)
    plt.xlabel('日期')
    plt.ylabel('累计净值-单位净值')
    plt.title('基金“分红”信息')
    plt.show()

    # 日增长率分析
    print('日增长率缺失：', sum(np.isnan(daily_growth_rate)))
    print('日增长率为正的天数：', sum(daily_growth_rate > 0))
    print('日增长率为负（包含0）的天数：', sum(daily_growth_rate <= 0))


# 主程序
# python -m fund_analysis.crawler --code 161725
# python -m fund_analysis.crawler --code 110022
if __name__ == "__main__":
    init_logger()
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str)
    args = parser.parse_args()
    if not args.code:
        logger.error("基金代码为空: --code xxxx")
        exit()
    main(args.code)

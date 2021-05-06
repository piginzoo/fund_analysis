import datetime
import logging
import os
from collections import namedtuple

import pandas as pd

from fund_analysis import const
from fund_analysis.const import FUND_DATA_DIR, DATE_FORMAT, COL_DATE

logger = logging.getLogger(__name__)


def load_fund_data(code):
    csv_path = os.path.join(FUND_DATA_DIR, "{}.csv".format(code))

    if not os.path.exists(csv_path):
        logger.error("数据文件 %s 不存在", csv_path)
        return None

    try:
        dateparse = lambda x: datetime.datetime.strptime(x, DATE_FORMAT)
        df = pd.read_csv(csv_path,
                         index_col=COL_DATE,
                         parse_dates=True,
                         date_parser=dateparse)
    except:
        logger.exception("解析[%s]基金数据失败", code)
        return None
    # logger.info("加载了[%s]数据，行数：%d", csv_path, len(df))
    return df


def load_bond_interest_data():
    csv_path = "data/db/bond_interest_CN1YR.db"

    try:
        dateparse = lambda x: datetime.datetime.strptime(x, '%Y年%m月%d日')
        df = pd.read_csv(csv_path,
                         sep="\t",
                         index_col='日期',
                         parse_dates=True,
                         date_parser=dateparse)
    except:
        logger.exception("解析数据失败")
        return None

    print(df.resample('M').mean())
    return df


# "000001","HXCZHH","华夏成长混合","混合型","HUAXIACHENGZHANGHUNHE"
FundRecord = namedtuple('FundRecord', ['code', 'name', 'type'])


def load_fund_list():
    """
    "000001","HXCZHH","华夏成长混合","混合型","HUAXIACHENGZHANGHUNHE"
    :return:
    """
    with open(const.FUND_LIST_FILE, "r", encoding='utf-8') as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
        lines = [l.replace("\"", "") for l in lines]

    funds = []
    for line in lines:
        fund_info = line.split(",")
        code = fund_info[0]
        name = fund_info[2]
        type = fund_info[3]
        funds.append(FundRecord(code=code, name=name, type=type))
    return funds

    logger.debug("加载了%d行Fund数据", len(lines))
    return funds


def save_fund_data(code, df):
    dir = FUND_DATA_DIR
    if not os.path.exists(dir):
        logger.debug("目录[%s]不存在，创建", dir)
        os.makedirs(dir)
    data_path = os.path.join(dir, "{}.csv".format(code))

    # reindex the date column and sort it
    df = df.sort_index()

    df.to_csv(data_path, index_label=COL_DATE)
    logger.debug("保存了[%s]", data_path)
    return data_path

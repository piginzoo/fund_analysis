import datetime
import logging
import os
from collections import namedtuple

import pandas as pd
from pandas import DataFrame

from fund_analysis import const
from fund_analysis.const import FUND_DATA_DIR, INDEX_DATA_DIR, DATE_FORMAT, COL_DATE

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
        if not df.index.is_unique:
            logger.warning("数据日期重复，删除掉重复日期")
            df = df.drop_duplicates(inplace=True)
    except:
        logger.exception("解析[%s]基金数据失败", code)
        return None
    # logger.info("加载了[%s]数据，行数：%d", csv_path, len(df))
    return df


def load_bond_interest_data(periods):
    """
    get the proper bond interests from the given periods
    :param periods:
    :return:
    """
    try:
        dateparse = lambda x: datetime.datetime.strptime(x, '%Y年%m月%d日')
        df = pd.read_csv(const.DB_FILE_BOND_INTEREST,
                         sep="\t",
                         index_col='日期',
                         parse_dates=True,
                         date_parser=dateparse)
    except:
        logger.exception("解析[%s]数据失败", const.DB_FILE_BOND_INTEREST)
        return None

    interestes = []
    for date in periods:
        _day_interestes = df['收盘'].loc[str(date)].values
        if len(_day_interestes) == 0: continue
        interestes.append([date, _day_interestes[0]])

    df = DataFrame(interestes, columns=['date', 'rate'])
    df.set_index(['date'], inplace=True)

    return df


def index_code_by_name(name):
    for code, index in const.INDEX.items():
        if index.name == name:
            return code
    return None


def load_index_data_by_name(name):
    code = index_code_by_name(name)
    path = os.path.join(const.INDEX_DATA_DIR, code + ".csv")
    try:
        dateparse = lambda x: datetime.datetime.strptime(x, const.DATE_FORMAT)
        df = pd.read_csv(path,
                         index_col='date',
                         parse_dates=True,
                         date_parser=dateparse)
        return df
    except:
        logger.exception("解析指数数据[%s]失败", path)
        return None


# "000001","HXCZHH","华夏成长混合","混合型","HUAXIACHENGZHANGHUNHE"
FundRecord = namedtuple('FundRecord', ['code', 'name', 'type'])


def load_fund_list(fund_types=None):
    """
    "000001","HXCZHH","华夏成长混合","混合型","HUAXIACHENGZHANGHUNHE"
    fund_type: 基金类型，汉字，如果是逗号分割，为多种类型
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
        if fund_types:
            fund_types = fund_type.split(",")
            for fund_type in fund_types:
                if type==fund_type:
                    funds.append(FundRecord(code=code, name=name, type=type))
        else:
            funds.append(FundRecord(code=code, name=name, type=type))
    return funds

    logger.debug("加载了%d行Fund数据", len(lines))
    return funds


def load_fund(code):
    fund_list = load_fund_list()
    for fund in fund_list:
        if fund.code == code: return fund
    return None


def save_fund_data(code, df):
    return save_data(FUND_DATA_DIR, "{}.csv".format(code), df)


def save_index_data(code, df):
    return save_data(INDEX_DATA_DIR, "{}.csv".format(code), df, index_label='date')


def filter_by_date(target_df, source_df):
    """
    用源source_df,去过滤，目标target_df，假设index都是日期
    """
    index = source_df.index
    return target_df.loc[index]


def calculate_rate(df, col_name):
    """根据日期，逐日计算利率：(day2-day1)/day1"""
    df['rate'] = df[col_name].diff()
    return df


def save_data(dir, file_name, df, index_label=None):
    if not os.path.exists(dir):
        logger.debug("目录[%s]不存在，创建", dir)
        os.makedirs(dir)
    data_path = os.path.join(dir, file_name)

    # reindex the date column and sort it
    if index_label: df.set_index([index_label], inplace=True)
    df = df.sort_index()

    df.to_csv(data_path, index_label=index_label)
    logger.debug("保存了[%s]", data_path)
    return data_path


# python -m fund_analysis.tools.date_utils
if __name__ == '__main__':
    print(load_bond_interest_data(const.PERIOD_YEAR))
    print("-----------------------------------")
    print(load_bond_interest_data(const.PERIOD_QUARTER))
    print("-----------------------------------")
    print(load_bond_interest_data(const.PERIOD_MONTH))
    print("-----------------------------------")
    print(load_bond_interest_data(const.PERIOD_WEEK))
    print("-----------------------------------")

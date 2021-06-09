import datetime
import logging
import os
from collections import namedtuple

import pandas as pd
from pandas import DataFrame, Series

from fund_analysis import const
from fund_analysis.bo.fund import Fund
from fund_analysis.const import FUND_DATA_DIR, INDEX_DATA_DIR, DATE_FORMAT, COL_DATE, STOCK_DIR, COL_RATE
from fund_analysis.tools import utils, date_utils, jqdata_utils
from fund_analysis.tools.date_utils import get_peroid

logger = logging.getLogger(__name__)


def load_fund_data(code):
    csv_path = os.path.join(FUND_DATA_DIR, "{}.csv".format(code))
    return load_csv_data(csv_path, index_col=COL_DATE)


def load_stock_data(code):
    code = jqdata_utils.get_market_code(code)
    csv_path = os.path.join(STOCK_DIR, "{}.csv".format(code))
    return load_csv_data(csv_path, index_col='date')


def load_csv_data(csv_path, index_col):
    if not os.path.exists(csv_path):
        logger.error("数据文件 %s 不存在", csv_path)
        return None

    try:
        dateparse = lambda x: datetime.datetime.strptime(x, DATE_FORMAT).date()
        df = pd.read_csv(csv_path,
                         index_col=index_col,
                         parse_dates=True,
                         date_parser=dateparse)
        if not df.index.is_unique:
            logger.warning("数据日期重复，删除掉重复日期")
            df = df.drop_duplicates(inplace=True)

        if df is None:
            logger.debug("加载基金数据 [%s] 为空", csv_path)

    except:
        logger.exception("解析[%s]数据失败", csv_path)
        return None
    # logger.info("加载了[%s]数据，行数：%d", csv_path, len(df))
    return df


def load_bond_interest_data(periods=None):
    """
    get the proper bond interests from the given periods
            收益率=债券利息/债券价格*100%，是指债券的回报率；简单说，债券价格是上下浮动，
            如果你买有1000元国债，年利率是5%，那么收益率是5%，如果价格变成950元，
            那么收益率=5%*1000/950*100%=5.26%，那么它的收益率上升，即收益率与债券价格是负相关。
            而年利率，也就是债券利息是一经发行就不会变的，而收益率是变化着的。
    :param periods:
    :return: 每天的收益率（百分比，比如 2 => 2% =>0.02）
    """
    try:
        dateparse = lambda x: datetime.datetime.strptime(x, '%Y年%m月%d日').date()
        df = pd.read_csv(const.DB_FILE_BOND_INTEREST,
                         sep="\t",
                         index_col='日期',
                         parse_dates=True,
                         date_parser=dateparse)
    except:
        logger.exception("解析[%s]数据失败", const.DB_FILE_BOND_INTEREST)
        return None

    # 按时间过滤
    if periods: df = df.loc[periods]

    # interestes = []
    # for date in periods:
    #     _day_interestes = df['收盘'].loc[str(date)].values
    #     if len(_day_interestes) == 0: continue
    #     interestes.append([date, _day_interestes[0]])
    # df = DataFrame(interestes, columns=['date', 'rate'])
    # df.set_index(['date'], inplace=True)

    df.sort_index(inplace=True)
    return df[['收盘']]


def index_code_by_name(name):
    for code, index in const.INDEX.items():
        if index.name == name:
            return code
    return None


def load_index_data_by_name(name, period=const.PERIOD_DAY):
    """
    按照基金名称加载指数数据
    """

    code = index_code_by_name(name)
    path = os.path.join(const.INDEX_DATA_DIR, code + ".csv")
    try:
        dateparse = lambda x: datetime.datetime.strptime(x, const.DATE_FORMAT).date()
        df = pd.read_csv(path,
                         index_col='date',
                         parse_dates=True,
                         date_parser=dateparse)

        index_data = calculate_rate(df, 'close', period)  # 把指数值转化成收益率，代表了市场r_m
        index_data.sort_index(inplace=True)
        return index_data
    except:
        logger.exception("解析指数数据[%s]失败", path)
        return None


# "000001","HXCZHH","华夏成长混合","混合型","HUAXIACHENGZHANGHUNHE"
FundRecord = namedtuple('FundRecord', ['code', 'name', 'type'])


def load_fund_list_from_db():
    session = utils.connect_database()
    funds = session.query(Fund).all()
    return funds


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
                if type == fund_type:
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


def calculate_rate(df, col_name, interval=const.PERIOD_DAY, calulate_by='price'):
    """
    根据日期，逐日计算利率：(day2-day1)/day1
    要求数据的索引，必须是日期类型的
    @:param interval 周期：日、周、月、年
    日，就是日，
    但是周、月、年，如果还要使用日期作为index的话，就要使用第一天做这周、这月、这年的收益率，
    这样做是为了统一，虽然听上去不合理，
    """
    # rate = (df[col_name] - df[col_name].shift(1)) / df[col_name].shift(1)
    # pct_change更好使

    if interval == const.PERIOD_DAY:
        if calulate_by == 'price':
            rate = df[col_name].pct_change() * 100  # <------ 全部使用%，所以要✖100
            rate.iloc[0] = 0  # 第一天收益率强制设为0
            df[COL_RATE] = rate
            return df[[COL_RATE]]
        else:
            df = df[[col_name]]
            df.columns = [COL_RATE]
            return df
    else:
        periods = []
        for year in range(const.PERIOD_START_YEAR, datetime.datetime.now().year + 1):
            periods += get_peroid(year, interval)

        # logger.debug("按照[%s]间隔，得到%d个时间区间",interval, len(periods))
        rate_dates = []
        rates = []
        for period in periods:
            start = period[0]
            end = period[1]
            period_data = df.loc[start:end]
            if len(period_data) == 0:
                # logger.debug("按[%r~%r]过滤出0条",start,end)
                continue
            # logger.debug("%r~%r:%d条",start,end,len(period_data))
            # logger.debug(period_data)
            if calulate_by == 'price':
                delta = period_data.iloc[-1][col_name] - period_data.iloc[0][col_name]
                rate = delta * 100 / period_data.iloc[0][col_name]  # 用百分比，所以✖100
            else:
                # 直接按照某一列算平均，这个是应对国债的情况，给出的就是利率了，不用你算了，所以去平均即可
                rate = period_data.mean().values[0]
                # logger.debug("国债：%r",rate)
            # logger.debug("date/rates:%s/%r", start, rate)
            rates.append(rate)
            rate_dates.append(start)
        # logger.debug("rates:%d",len(rates))
        df = DataFrame(rates, columns=[COL_RATE], index=rate_dates)
        df.index = pd.to_datetime(df.index)  # 转成日期类型的index
        return df

def join(df1, df2):
    if type(df1) == Series: df1 = df1.to_frame()
    if type(df2) == Series: df2 = df2.to_frame()
    df12 = df1.join(df2, how="inner", lsuffix="d_")
    return df12.iloc[:, 0], df12.iloc[:, 1]


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


def merge_by_date(df_list: list, selected_col_names=None, new_col_names=None):
    """
    按照日期合并几个dataframe，只有日期相同的记录留下来
    他们都必须使用date日期类型做index
    """

    if selected_col_names:
        assert len(selected_col_names) == len(df_list)
        df_list = [df[name] for df, name in zip(df_list, selected_col_names)]

    for df in df_list:
        logger.debug("开始[%r]~结束[%r]", date_utils.date2str(df.index[0]), date_utils.date2str(df.index[-1]))

    result = pd.concat(df_list, axis=1)
    result = result.dropna(how="any", axis=0)
    if len(result) == 0:
        logger.warning("按照时间过滤后，记录剩余条数为0")
        return result
    logger.debug("开始[%r]~结束[%r] <----- 合并后", date_utils.date2str(result.index[0]),
                 date_utils.date2str(result.index[-1]))

    if new_col_names: result.columns = new_col_names

    return result


# python -m fund_analysis.tools.data_utils
if __name__ == '__main__':
    utils.init_logger()
    df = load_fund_data('519778')

    df_result = calculate_rate(df, const.COL_ACCUMULATIVE_NET, const.PERIOD_DAY)
    logger.debug("日收益：%r~%r, %d天", df_result.index[0], df_result.index[-1], len(df_result))
    logger.debug(df_result)

    logger.debug("------------------------------")

    df_result = calculate_rate(df, const.COL_ACCUMULATIVE_NET, const.PERIOD_WEEK)
    logger.debug("周收益：%r~%r, %d周", df_result.index[0], df_result.index[-1], len(df_result))
    logger.debug(df_result)

    logger.debug("------------------------------")

    df_result = calculate_rate(df, const.COL_ACCUMULATIVE_NET, const.PERIOD_MONTH)
    logger.debug("月收益：%r~%r, %d月", df_result.index[0], df_result.index[-1], len(df_result))
    logger.debug(df_result)

    logger.debug("------------------------------")

    df_result = calculate_rate(df, const.COL_ACCUMULATIVE_NET, const.PERIOD_YEAR)
    logger.debug("年收益：%r~%r, %d年", df_result.index[0], df_result.index[-1], len(df_result))
    logger.debug(df_result)

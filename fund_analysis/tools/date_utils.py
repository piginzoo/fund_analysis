import calendar
import datetime

from dateutil.relativedelta import *

from fund_analysis import const
from fund_analysis.const import DATE_FORMAT


def str2date(date_str):
    return datetime.datetime.strptime(date_str, DATE_FORMAT).date()


def date2str(date):
    return date.strftime(DATE_FORMAT)


def is_date(text):
    try:
        dt = datetime.datetime.strptime(text, DATE_FORMAT)
        return True
    except ValueError:
        return False


def interval_days(from_date, end_date):
    """
    :param from_date: 格式 2021-04-01
    :param end_date:
    :return:
    """
    date_from = datetime.datetime.strptime(from_date, DATE_FORMAT)
    date_end = datetime.datetime.strptime(end_date, DATE_FORMAT)
    interval = date_end - date_from  # 两日期差距
    return interval.days


def get_yesterday():
    return get_days_from_now(1)


def get_days_from_now(num):
    """返回从今天开始往前数num天的日期"""
    today = datetime.datetime.now()
    start_date = today - datetime.timedelta(days=num)
    return start_date.date()  # .date() to reset the time to midnight(00:00)


def get_days(from_date, to_date):
    if type(from_date) == str:
        from_date = str2date(from_date)
    if type(to_date) == str:
        to_date = str2date(to_date)
    delta = to_date - from_date
    return delta.days


def today():
    today = datetime.datetime.now()
    return date2str(today)


def get_peroid(year, period):
    """
    return the star&end date by period
    :param year: which year
    :param period: week,month,quarter,year
    :return: a list< [start_date, end_date] >
    """
    if period == const.PERIOD_YEAR:
        return [[str2date(str(year) + "-1-1"), str2date(str(year) + "-12-31")]]

    result = []
    if period == const.PERIOD_MONTH:
        for month in range(1, 13):
            weekday, days = calendar.monthrange(year, month)
            start_date = str(year) + "-" + str(month) + "-1"
            end_date = str(year) + "-" + str(month) + "-" + str(days)
            result.append([str2date(start_date), str2date(end_date)])
        return result

    if period == const.PERIOD_QUARTER:
        quarter_months = [1, 3, 6, 9, 12]
        for i in range(len(quarter_months) - 1):
            start_month = quarter_months[i]
            end_month = quarter_months[i + 1]
            weekday, days = calendar.monthrange(year, end_month)
            start_date = str(year) + "-" + str(start_month) + "-1"
            end_date = str(year) + "-" + str(end_month) + "-" + str(days)
            result.append([str2date(start_date), str2date(end_date)])
        return result

    if period == const.PERIOD_WEEK:
        weekday, _ = calendar.monthrange(year, 1)  # 1月
        start_date = str2date(str(year) + "-1-" + str(7 - weekday))
        for i in range(1, 52):
            end_date = start_date + relativedelta(start_date, weeks=+1)
            true_end_date = end_date + relativedelta(end_date, days=-1)
            result.append([start_date, true_end_date])
            start_date = end_date

        return result




# python -m fund_analysis.date_utils
if __name__ == '__main__':
    assert interval_days('1998-9-1', '2021-04-01') == 8248
    assert interval_days('2021-4-1', '2021-04-10') == 9
    print(get_peroid(2020, 'year'))
    print("-----")
    print(get_peroid(2020, 'quarter'))
    print("-----")
    print(get_peroid(2020, 'month'))
    print("-----")
    print(get_peroid(2020, 'week'))

"""
This implement the investment plans profit calculation.

You need create a analysis plan in the folder "<data/plan/xxx.txt>",
and you can run the <bin/analysis.sh> to calculate your profit by providing the file name.

the file format is like this:
```
    date,+/-amount
    example: 2019-3-18,1000 <-- means analysis 1000$ more
             2020-1-5, -2500 <-- means withdraw 2500$
```
there still some special format for money analysis description:
- month_X,<amount>
- week_X,<amount>
which means, the day for each week or month, I will analysis more money, whose amount is <amount>.
but if any items below the format contents, means, there are some new break for the routine investment.
below is the complete example:
```
    2020-1-7,5000
    2020-1-13,5000
    2020-2.24,-3231
    month_10,1000
```
"""
import io
import logging
import os
from collections import namedtuple
from datetime import datetime, timedelta

from fund_analysis import const
from fund_analysis.const import DATE_FORMAT
from fund_analysis.tools import utils

logger = logging.getLogger(__name__)

InvestRecord = namedtuple('InvestRecord', ['date', 'amount'])


def parse_successor_date(period, day, previous_line, next_line, amount):
    """
    calcuate the successor date util the next_date
    :param period:
    :param day:
    :param next_date: the next line of stop date
    :param amount:
    :return: return all analysis day and its amount
    """
    previous_date_str, _ = previous_line.split(",")
    previous_date = datetime.strptime(previous_date_str, DATE_FORMAT)
    next_date_str, _ = next_line.split(",")
    next_date = datetime.strptime(next_date_str, DATE_FORMAT)

    delta = next_date - previous_date
    records = []
    for i in range(delta.days + 1):

        date = previous_date + timedelta(days=i)
        date_str = datetime.strftime(date, DATE_FORMAT)

        if period == const.PERIOD_MONTH and date.day == day:
            logger.debug("%d月%d日，定投:%f", date.month, date.day, amount)
            records.append(InvestRecord(date=utils.str2date(date_str), amount=amount))
        if period == const.PERIOD_WEEK and date.weekday() + 1 == day:
            logger.debug("每周%d(%s)，定投:%f", day, date_str, amount)
            records.append(InvestRecord(date=utils.str2date(date_str), amount=amount))
        if period == const.PERIOD_DAY:
            records.append(InvestRecord(date=utils.str2date(date_str), amount=amount))

    return records


def load(file_path):
    if not os.path.exists(file_path):
        logger.error("投资计划文件[%s]不存在")
        return None
    f_stream = open(file_path, "r", encoding='utf-8')
    return load_stream(f_stream)


def load_stream(steam):
    """
    2020-1-7, 5000
    2020-1-13, 5000
    2020-2-24, -3231
    month_10, 1000
    2021-1-18, -5000
    week_2, 800
    """
    records = []

    lines = steam.readlines()
    lines = [l.strip() for l in lines if l.strip() != ""]

    for i, line in enumerate(lines):
        if line.startswith("#"): continue # ignore the comments
        date_str, amount = line.split(",")
        amount = float(amount)

        if utils.is_date(date_str):
            records.append(InvestRecord(date=utils.str2date(date_str), amount=amount))
            logger.debug("%s日，定投:%f", date_str, amount)
            continue

        # month_10 => month , 10
        if date_str.startswith(const.PERIOD_MONTH) or \
                date_str.startswith(const.PERIOD_WEEK) or \
                date_str.startswith(const.PERIOD_DAY):
            period, day = date_str.split("_")
            day = int(day)
            amount = float(amount)

            # if i am have next brother, use it to terminate me
            if i < len(lines) - 1:
                previous_line = lines[i - 1]
                next_line = lines[i + 1]
                next_date_str, _ = next_line.split(",")
                if next_date_str is None:
                    logger.error("不合规的文件格式：%r", lines)
                    raise ValueError("不合规的文件格式：\r" + str(lines))
                records += parse_successor_date(period, day, previous_line, next_line, amount)
            else:  # if i am the last line
                previous_line = lines[i - 1]
                yesterday = datetime.now() - timedelta(days=1)
                fake_yesterday_line = yesterday.strftime('%Y-%m-%d') + ",0"
                records += parse_successor_date(period, day, previous_line, fake_yesterday_line, amount)
    return records


# python -m fund_analysis.analysis.plan_loader
if __name__ == '__main__':
    utils.init_logger()
    stream = io.StringIO(
        """
        2020-1-7, 5000
        2020-1-13, 5000
        2020-2-24, -3231
        month_10, 1000
        2021-1-18, -5000
        week_2, 800
        """)
    records = load_stream(stream)
    logger.debug("所有的记录：%r", records)

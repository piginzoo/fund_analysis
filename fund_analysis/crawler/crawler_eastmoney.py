# 导入需要的模块
import random
import re
import time

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

from fund_analysis.const import NUM_PER_PAGE
from fund_analysis.crawler.crawler import Crawler
from fund_analysis.tools.data_utils import load_fund_data, save_fund_data
from fund_analysis.tools.utils import *

logger = logging.getLogger(__name__)


class EastmoneyCrawler(Crawler):

    def crawle_one(self, code):
        total_data = load_fund_data(code)

        start_date, end_date = self.get_start_end_date(code, total_data)

        if start_date is None and end_date is None:
            logger.info("爬取失败[%s]，原因：无法获得起止日期", code)
            return

        if start_date == end_date:
            logger.info("无需爬取[%s]，原因：开始和结束日期[%r]一样", code, start_date)
            return

        logger.info("准备爬取 [%s] --> [%s] 的数据", start_date, end_date)

        page_num = self.get_page_num(code, start_date, end_date)

        for i in range(1, page_num + 1):

            html = self.get_content(code, i, NUM_PER_PAGE, start_date, end_date)

            data = self.parse_html(html)

            if data is None:
                continue

            # 修改数据类型
            data[COL_DATE] = pd.to_datetime(data[COL_DATE], format='%Y/%m/%d')
            data.set_index(COL_DATE, inplace=True)
            data['单位净值'] = data['单位净值'].astype(float)
            data['累计净值'] = data['累计净值'].astype(float)
            data['日增长率'] = data['日增长率'].str.strip('%').astype(float)

            if total_data is None:
                total_data = data
                logger.debug("基金[%s]不存在，创建[%d]条", code, len(data))
            else:
                total_data = total_data.append(data)
                # print(total_data)

                logger.debug("追加[%d]条到基金[%s]中，合计[%d]条", len(data), code, len(total_data))

            time.sleep(random.random() * 1)
            logger.info("已爬完第%d页数据，准备爬取第%d页", i, i + 1)

        if total_data is None:
            logger.error("代码 [%s] 爬取失败!!!")
            return

        data_path = save_fund_data(code, total_data)
        logger.info("保存%d行所有数据，到[%s]中", len(total_data), data_path)

    def get_content(self, code, page, num_per_page=NUM_PER_PAGE, sdate=None, edate=None):
        """
        xxxx,records:2570,pages:65,xxx
        获得整个页数
        """
        if sdate:
            url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={}&page={}&per={}&sdate={}&edate={}'.format(
                code, page, num_per_page, sdate, edate)
        else:
            url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={}&page={}&per={}'.format(
                code, page, num_per_page)
        html = get_url(url)
        return html

    def get_page_num(self, code, sdate=None, edate=None):
        html = self.get_content(code, 1, NUM_PER_PAGE, sdate, edate)

        # 获取总页数
        pattern = re.compile(r'pages:(.*),')
        result = re.search(pattern, html).group(1)
        page_num = int(result)
        logger.info("获得 代码[%s]的信息：共有 %d 页，每页 %d 条，开始日期：%r，结束日期：%r", code, page_num, NUM_PER_PAGE, sdate, edate)
        return int(page_num)

    def get_latest_day(self, df):
        return df.index[-1]

    def get_start_end_date(self, code, df):
        if df is None:
            num = self.get_page_num(code)

            if num == 0:
                logger.debug("无法从页面中提取爬取的天数，天数为0")
                return None, None

            _end = get_yesterday()
            _from = get_days_from_now(num * NUM_PER_PAGE)
            logger.info("第一次爬取，共[%d]条，从[%s]-->[%s]", num, _from, _end)
            return _from, _end

        latest_day = self.get_latest_day(df)
        logger.info("断点续爬：爬取从今天 (%r) -> (%r) 的数据", latest_day, get_yesterday())
        return latest_day, get_yesterday()

    # 从网页抓取数据
    def parse_html(self, html):
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

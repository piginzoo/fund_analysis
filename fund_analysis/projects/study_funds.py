import argparse
import os
from collections import namedtuple
from queue import Empty

from fund_analysis.analysis.calculate_TM import TMCalculater
from fund_analysis.analysis.calculate_show import ShowCalculater
from fund_analysis.crawler.fund.crawler_eastmoney import EastmoneyCrawler
from fund_analysis.crawler.fund.crawler_eastmoney_fund_manager import EastmoneyFundManagerCrawler
from fund_analysis.crawler.fund.crawler_jqdata_fund import JQDataFundCrawler
from fund_analysis.tools.multi_processor import execute
from fund_analysis.tools.utils import init_logger

tm_calculator = TMCalculater()
basic_calculator = ShowCalculater()

FILE_DIR = "fund_analysis/projects/schema"

Result = namedtuple('Result', ['code', 'name', 'start', 'year', 'alpha', 'beta2', 'profit', 'aagr', 'withdraw'])
Fund = namedtuple('Fund', ['code', 'name', 'manager', 'company'])
import logging

logger = logging.getLogger(__name__)

init_logger()


def load_fund_list(file_name):
    """
    基金代码|基金名称|基金经理|基金公司
    —————————————————————————————
    110011,易方达中小盘,张坤,易方达
    """
    full_path = os.path.join(FILE_DIR, file_name)
    if not os.path.exists(full_path):
        logger.warning("基金列表文件[%s]不存在", full_path)
        return None
    with open(full_path, "r", encoding='utf-8') as f:
        lines = f.readlines()
    funds = []
    for line in lines:
        if line.strip().startswith("#"): continue  # 忽略注释
        line = line.strip()
        commend_pos = line.find("#")
        if commend_pos != -1:
            line = line[:commend_pos].strip()
        fund_info = line.split(",")
        code = fund_info[0]
        name = fund_info[1]
        manager = fund_info[2] if len(fund_info) > 2 else ''
        company = fund_info[3] if len(fund_info) > 3 else ''
        fund = Fund(code=code, name=name, manager=manager, company=company)
        funds.append(fund)

    return funds


def update_fund(code):
    """
    更新基金信息：
    - 基金的基本信息
    - 基金的交易信息
    - 基金经理信息
    """
    logger.info("更新基金基本信息")
    JQDataFundCrawler().crawle_one(code, True)
    logger.info("更新基金交易信息")
    EastmoneyCrawler().crawle_one(code, True)
    logger.info("更新基金经理信息")
    EastmoneyFundManagerCrawler().crawle_one(code, True)


def format(results):
    logger.debug(
        "=====================================================================================================================")

    logger.debug(
        "| {1:^8} | {2:{0}^15} | {3:^8} | {4:^4} | {5:^6} |  {6:^6} |  {7:^4} |  {8:^4} |  {9:^4} |".format(
            chr(12288), "Code", "名称", "开始", "年限", "α", "β2", "总收益", "年化收益", "最大回撤"
        )
    )

    for r in results:
        # print(r.code,
        #       r.name,
        #       r.alpha,
        #       r.beta2,
        #       r.profit * 100,
        #       r.aagr * 100,
        #       r.withdraw * 100
        #       )
        logger.debug(
            "---------------------------------------------------------------------------------------------------------------------")

        str_r = "| {1:^8} | {2:{0}^15} | {3:^8} | {4:^6.1f} | {5:^6.2%} |  {6:^6.2%} |  {7:^6.2%} |  {8:^8.2%} |  {9:^8.2%} |".format(
            chr(12288),
            r.code,
            r.name,
            r.start,
            r.year,
            r.alpha,
            r.beta2,
            r.profit,
            r.aagr,
            r.withdraw
        )
        logger.debug(str_r)
    logger.debug(
        "=====================================================================================================================")


def process(fund, id, queue):
    args = "--code {} --type fund --period week --index 上证指数".format(fund.code)
    x, y, pred, alpha, beta1, beta2 = tm_calculator.process(args)
    args = "--code {}".format(fund.code)
    data, index_close_price, max_withdraw, start, year, aagr, total_profit = \
        basic_calculator.process(args)
    logger.debug("[%s],α=%.4f,β2=%.4f", fund.code, alpha, beta2)
    logger.debug(
        "-----------------------------------------------------------------------------------------------------")
    queue.put(Result(
        fund.code,
        fund.name,
        start,
        year,
        alpha,
        beta2,
        total_profit,
        aagr,
        max_withdraw))


# python -m fund_analysis.projects.study_funds --funds cmb_recommend.txt --update
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--funds', '-f', type=str, default=None)
    parser.add_argument('--update', '-u', action='store_true', dest="update", default=False, help="是否再次强制爬取，覆盖已有的")
    args = parser.parse_args()
    funds = load_fund_list(args.funds)
    if funds is None: exit()

    if args.update:
        logger.info("更新各个基金信息")
        for fund in funds:
            update_fund(fund.code)

    queue = execute(funds, worker_num=4, function=process)
    results = []
    while True:
        try:
            # https://my.oschina.net/yangyanxing/blog/296052
            data = queue.get_nowait()
            results.append(data)
        except Empty:
            logger.info("队列已空，全部取完！")
            break
    format(results)

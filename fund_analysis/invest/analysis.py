# python -m fund_analysis.invest.calculate_sharpe --code 519778 --asset 10 --period month
import argparse
import logging
import time

from tqdm import tqdm

from fund_analysis import const
from fund_analysis.bo.fund import FundStock, StockIndustry
from fund_analysis.bo.fund_analysis import FundAnalysis
from fund_analysis.invest.calculate_sharpe import calculate_one_fund
from fund_analysis.tools import utils, data_utils

logger = logging.getLogger(__name__)


def main(code, force):
    session = utils.connect_database()

    fund_list = data_utils.load_fund_list()

    if code:
        fund = data_utils.load_fund(code)
        handle_one_fund(fund, session)
    else:
        pbar = tqdm(total=len(fund_list))
        counter = 0
        error = 0
        start = time.time()
        for fund in fund_list:
            try:
                handle_one_fund(fund, session, force)
            except:
                logger.exception("处理 [%s] 失败...", fund.code)
                error += 1
                continue
            counter += 1
            pbar.update(1)
        pbar.close()
        end = time.time()

        logger.info("合计处理[%d]条，[%d]失败，[%d]成功，平均耗时：%.2f 秒/条",
                    counter,
                    error,
                    counter - error,
                    (end - start) / counter)


def handle_one_fund(fund, session, force=True):
    fund_analysis = session.query(FundAnalysis).filter(FundAnalysis.code == fund.code).limit(1).first()

    if not force and fund_analysis:
        logger.info("[%s:%s] 记录已存在，忽略", fund.code, fund.name)
        return

    create = False
    if fund_analysis is None:
        create = True
        fund_analysis = FundAnalysis()

    fund_stock_industries = session.query(FundStock, StockIndustry). \
        filter(FundStock.fund_code == fund.code). \
        filter(FundStock.stock_code == StockIndustry.stock_code). \
        order_by(FundStock.proportion.desc()). \
        limit(1).all()

    industry_name = None
    industry_code = None
    if len(fund_stock_industries) == 1:
        fund_stock, stock_industry = fund_stock_industries[0]
        industry_name = stock_industry.industry_name
        industry_code = stock_industry.industry_code

    sharpe_ratios = calculate_one_fund(fund, const.FUND_MINIMUM_ASSET, const.PERIOD_ALL, session)
    if sharpe_ratios is None:
        # its not mix & stock fund
        return

    fund_analysis.code = fund.code
    fund_analysis.name = fund.name
    fund_analysis.sharpe_year = sharpe_ratios[0]
    fund_analysis.sharpe_quarter = sharpe_ratios[1]
    fund_analysis.sharpe_month = sharpe_ratios[2]
    fund_analysis.sharpe_week = sharpe_ratios[3]
    fund_analysis.industry_code = industry_code
    fund_analysis.industry_name = industry_name

    if create:
        session.add(fund_analysis)
        session.commit()
    else:
        logger.debug("更新")
        session.flush()
        session.commit()


# python -m fund_analysis.invest.analysis --code 519778
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str, default=None)
    parser.add_argument('--force', '-f', type=str, action='store_true', default=False)
    args = parser.parse_args()
    code = args.code

    utils.init_logger(logging.INFO)
    main(args.code, force=args.force)

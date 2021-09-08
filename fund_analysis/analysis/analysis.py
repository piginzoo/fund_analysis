# python -m fund_analysis.analysis.calculate_sharpe --code 519778 --asset 10 --period month
import argparse
import logging
import time

from tqdm import tqdm

from fund_analysis import const
from fund_analysis.bo.fund import FundStock, StockIndustry
from fund_analysis.bo.fund_beta import FundBeta
from fund_analysis.bo.fund_industry import FundIndustry
from fund_analysis.bo.fund_sharpe import FundSharpe
from fund_analysis.analysis import calculate_beta
from fund_analysis.analysis.calculate_sharpe import calculate_one_fund
from fund_analysis.tools import utils, data_utils

logger = logging.getLogger(__name__)

"""
不是用于展示，而是用于计算，跑一遍所有的基金，挨个计算beta，行业，夏普指数
- beta，用的是估值，而是用的是定义（协方差），而没用回归
- 行业，直接去找了10大股票中，最大的一只的股票的行业归属
- 夏普，分别计算了年、季、月的夏普指数
"""
def main(code):
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
                handle_one_fund(fund, session=False)
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

def handle_beta(fund,session):

    for _,index in const.INDEX.items():

        fund_beta = session.query(FundBeta).filter(
            FundBeta.code == fund.code and FundBeta.index_code == index.code).limit(1).first()

        is_create = False
        if fund_beta is None:
            is_create = True
            fund_beta = FundBeta()
            fund_beta.code = fund.code
            fund_beta.name = fund.name

        fund_beta.beta,_ = calculate_beta.calculate_by_cov(fund.code,const.FUND,const.PERIOD_DAY,index.name)
        fund_beta.index_name = index.name
        fund_beta.index_code = index.code

        logger.info("基于指数[%s]计算的beta值：%.3f%%", index.name, fund_beta.beta)

        save_or_update(session, fund_beta, is_create)

def handle_industry(fund,session):
    fund_industry = session.query(FundIndustry).filter(FundIndustry.code == fund.code).limit(1).first()

    is_create = False
    if fund_industry is None:
        is_create = True
        fund_industry = FundIndustry()
        fund_industry.code = fund.code
        fund_industry.name = fund.name

    fund_stock_industries = session.query(FundStock, StockIndustry). \
        filter(FundStock.fund_code == fund.code). \
        filter(FundStock.stock_code == StockIndustry.stock_code). \
        order_by(FundStock.proportion.desc()). \
        limit(1).all()

    if len(fund_stock_industries) == 1:
        fund_stock, stock_industry = fund_stock_industries[0]
        fund_industry.industry_name = stock_industry.industry_name
        fund_industry.industry_code = stock_industry.industry_code

        logger.debug("基金所属行业：%s", fund_industry.industry_name)

        save_or_update(session,fund_industry,is_create)

def handle_sharp(fund,session):

    fund_sharpe = session.query(FundSharpe).filter(FundSharpe.code == fund.code).limit(1).first()

    is_create = False
    if fund_sharpe is None:
        is_create = True
        fund_sharpe = FundSharpe()
        fund_sharpe.code = fund.code
        fund_sharpe.name = fund.name

    sharpe_ratios = calculate_one_fund(fund, 0, const.PERIOD_ALL, session)
    if sharpe_ratios is None: return

    fund_sharpe.sharpe_year = sharpe_ratios[0]
    fund_sharpe.sharpe_quarter = sharpe_ratios[1]
    fund_sharpe.sharpe_month = sharpe_ratios[2]
    fund_sharpe.sharpe_week = sharpe_ratios[3]

    save_or_update(session, fund_sharpe, is_create)

def handle_one_fund(fund, session):
    logger.info("--------------------------------------------------------")
    handle_beta(fund,session)
    logger.info("--------------------------------------------------------")
    handle_sharp(fund, session)
    logger.info("--------------------------------------------------------")
    handle_industry(fund, session)


def save_or_update(session, dbo, is_create):
    if is_create:
        session.add(dbo)
        session.commit()
    else:
        # logger.debug("更新")
        session.flush()
        session.commit()

# python -m fund_analysis.analysis.analysis --code 519778
if __name__ == '__main__':
    """
    --code 基金代码
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str, default=None)
    args = parser.parse_args()
    code = args.code

    utils.init_logger(logging.DEBUG)
    main(args.code)

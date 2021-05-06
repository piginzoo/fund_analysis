import logging

from tqdm import tqdm

from fund_analysis import crawler
from fund_analysis.tools.utils import load_fund_list

logger = logging.getLogger(__name__)


def main():
    fund_list = load_fund_list()

    pbar = tqdm(total=len(fund_list))
    for fund in fund_list:
        try:
            crawler.main(fund.code)
        except:
            logger.info("爬取 [%s] : %s 失败！！！", fund.code, fund.name)
        logger.info("爬取 [%s] : %s 完成", fund.code, fund.name)
        pbar.update(1)
    pbar.close()


# python -m fund_analysis.main
if __name__ == '__main__':
    utils.init_logger()
    main()
